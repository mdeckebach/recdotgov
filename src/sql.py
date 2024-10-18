CREATE_FCT_AVAILABILITY_SNAPSHOTS_IF_NOT_EXISTS = '''
    CREATE TABLE IF NOT EXISTS fct_availability_snapshots (
        id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
        entry_id varchar(50) DEFAULT NULL,
        permit_id varchar(50) DEFAULT NULL,
        reservation_ds varchar(50) DEFAULT NULL,
        available int(11) DEFAULT NULL,
        reserved int(11) DEFAULT NULL,
        total int(11) DEFAULT NULL,
        is_walkup tinyint(4) DEFAULT NULL,
        not_yet_released tinyint(4) DEFAULT NULL,
        release_ts varchar(50) DEFAULT NULL,
        snapshot_ts timestamp NULL DEFAULT NULL,
        _updated_ts timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
        PRIMARY KEY (id)
    );
'''

INSERT_SNAPSHOT = '''
    INSERT INTO fct_availability_snapshots (
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
    FROM fct_availability_snapshots
    WHERE id IN (
        SELECT MAX(id) 
        FROM fct_availability_snapshots
        GROUP BY entry_id, permit_id, reservation_ds
        );
'''

CREATE_DIM_ENTRY_POINTS_IF_NOT_EXISTS = '''
    CREATE TABLE IF NOT EXISTS dim_entry_points (
        entry_id varchar(50) NOT NULL,
        permit_id varchar(50) DEFAULT NULL,
        entry_code varchar(50) DEFAULT NULL,
        name varchar(50) DEFAULT NULL,
        description mediumtext DEFAULT NULL,
        district varchar(50) DEFAULT NULL,
        latitude decimal(20,6) DEFAULT NULL,
        longitude decimal(20,6) DEFAULT NULL,
        version varchar(50) DEFAULT NULL,
        modified_ts timestamp NULL DEFAULT NULL,
        _updated_ts timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
        PRIMARY KEY (entry_id)
    );
'''

# change to dim_entry_points
REPLACE_ENTRY_POINTS = '''
    REPLACE INTO dim_entry_points (
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