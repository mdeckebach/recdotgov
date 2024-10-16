INSERT_SNAPSHOT = '''
        INSERT INTO wilderness_permit_snapshots (
            entry_id,
            permit_id,
            reservation_ds,
            available,
            reserved,
            total,
            is_walkup,
            not_yet_released,
            release_ts,
            snapshot_ts)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''

SELECT_LATEST_SNAPSHOTS = '''
        SELECT
            entry_id,
            permit_id,
            reservation_ds,
            available,
            reserved,
            total,
            is_walkup,
            not_yet_released,
            release_ts
        FROM wilderness_permit_snapshots
        WHERE id IN (
            SELECT MAX(id) 
            FROM wilderness_permit_snapshots
            GROUP BY entry_id, permit_id, reservation_ds
            );
    '''

REPLACE_ENTRY_POINTS = '''
        REPLACE INTO entry_points (
            entry_code,
            description,
            district,
            entry_id,
            latitude,
            longitude,
            modified_ts,
            name,
            permit_id,
            version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''