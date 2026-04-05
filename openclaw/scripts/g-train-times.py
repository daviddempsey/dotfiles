#!/usr/bin/env python3
"""
Fetch G train arrival times at Nassau Ave station and L train connections
"""
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from nyct_gtfs import NYCTFeed

TRANSFER_TIME_MINUTES = 3  # Minimum transfer time at Metropolitan Ave
WALK_TO_STATION_MINUTES = 5  # Walk time from home to Nassau Ave

def get_train_times():
    """Get next G trains at Nassau Ave and L train connections at Metropolitan"""
    try:
        # Load G and L train feeds
        g_feed = NYCTFeed("G")
        l_feed = NYCTFeed("L")

        # Station IDs
        nassau_ave_g = "G32N"  # G train at Nassau Ave (northbound)
        metropolitan_g = "G29N"  # G train at Metropolitan Ave (northbound)
        metropolitan_l = "L24N"  # L train at Metropolitan Ave (toward Manhattan)

        # Get current time in Eastern
        et_tz = ZoneInfo("America/New_York")
        now_et = datetime.now(et_tz)

        # Collect G train times at Nassau Ave and Metropolitan Ave
        g_trains = []
        for trip in g_feed.trips:
            if trip.route_id != "G":
                continue

            nassau_time = None
            metro_time = None

            for stop_update in trip.stop_time_updates:
                if stop_update.stop_id == nassau_ave_g and stop_update.arrival:
                    nassau_time = stop_update.arrival.astimezone(et_tz)
                elif stop_update.stop_id == metropolitan_g and stop_update.arrival:
                    metro_time = stop_update.arrival.astimezone(et_tz)

            # Only include trains that stop at both stations
            if nassau_time and metro_time:
                minutes_until = int((nassau_time.timestamp() - now_et.timestamp()) / 60)
                if 0 <= minutes_until <= 45:  # Next 45 minutes
                    g_trains.append({
                        'nassau_time': nassau_time,
                        'metro_time': metro_time,
                        'minutes_until': minutes_until
                    })

        # Sort by Nassau Ave arrival
        g_trains.sort(key=lambda x: x['nassau_time'])

        # Collect L train times at Metropolitan Ave
        l_trains = []
        for trip in l_feed.trips:
            if trip.route_id != "L":
                continue

            for stop_update in trip.stop_time_updates:
                if stop_update.stop_id == metropolitan_l and stop_update.arrival:
                    arrival_et = stop_update.arrival.astimezone(et_tz)
                    minutes_until = int((arrival_et.timestamp() - now_et.timestamp()) / 60)
                    if 0 <= minutes_until <= 60:  # Next hour
                        l_trains.append({
                            'time': arrival_et,
                            'minutes_until': minutes_until
                        })

        # Sort L trains by time
        l_trains.sort(key=lambda x: x['time'])

        # Match G trains to L trains
        connections = []
        for g_train in g_trains[:5]:  # Check next 5 G trains
            # Find first L train that arrives at least TRANSFER_TIME_MINUTES after G arrives at Metropolitan
            earliest_l_time = g_train['metro_time'] + timedelta(minutes=TRANSFER_TIME_MINUTES)

            matching_l = None
            for l_train in l_trains:
                if l_train['time'] >= earliest_l_time:
                    matching_l = l_train
                    break

            connections.append({
                'g_nassau': g_train['nassau_time'],
                'g_metro': g_train['metro_time'],
                'g_minutes': g_train['minutes_until'],
                'l_metro': matching_l['time'] if matching_l else None,
                'l_minutes': matching_l['minutes_until'] if matching_l else None,
                'wait_time': int((matching_l['time'].timestamp() - g_train['metro_time'].timestamp()) / 60) if matching_l else None
            })

        # Get feed update times
        g_updated = g_feed.last_generated.astimezone(et_tz).strftime('%I:%M %p')
        l_updated = l_feed.last_generated.astimezone(et_tz).strftime('%I:%M %p')

        return {
            'connections': connections,
            'g_updated': g_updated,
            'l_updated': l_updated
        }

    except Exception as e:
        return {'error': str(e)}

def format_output(data):
    """Format the train connections for display"""
    if 'error' in data:
        return f"❌ Error fetching train times: {data['error']}"

    output = []
    output.append(f"🚇 G→L Train Connections (Nassau Ave → Metropolitan → Manhattan)")
    output.append(f"   G updated: {data['g_updated']} | L updated: {data['l_updated']}")
    output.append("")

    if not data['connections']:
        output.append("No connections found in the next hour")
        return "\n".join(output)

    for i, conn in enumerate(data['connections'], 1):
        g_time = conn['g_nassau'].strftime('%I:%M %p')
        g_metro_time = conn['g_metro'].strftime('%I:%M')
        leave_home = (conn['g_nassau'] - timedelta(minutes=WALK_TO_STATION_MINUTES)).strftime('%I:%M %p')

        if conn['l_metro']:
            l_time = conn['l_metro'].strftime('%I:%M')
            wait = conn['wait_time']

            # Format connection
            output.append(f"{i}. Leave home by: {leave_home}")
            output.append(f"   ├─ Leave Nassau: {g_time} ({conn['g_minutes']} min)")
            output.append(f"   └─ Arrive Metro: {g_metro_time} → L train: {l_time} ({wait} min wait)")
        else:
            output.append(f"{i}. Leave home by: {leave_home}")
            output.append(f"   ├─ Leave Nassau: {g_time} ({conn['g_minutes']} min)")
            output.append(f"   └─ Arrive Metro: {g_metro_time} → ⚠️  No L connection within transfer time")

        output.append("")

    return "\n".join(output)

if __name__ == "__main__":
    data = get_train_times()
    print(format_output(data))
