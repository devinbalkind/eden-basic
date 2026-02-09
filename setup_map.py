
try:
    import sys
    
    # Load models
    db = current.db
    s3db = current.s3db
    
    ctable = s3db.gis_config
    ptable = s3db.gis_projection
    ltable = s3db.gis_layer_config
    otable = s3db.gis_layer_openstreetmap
    etable = s3db.gis_layer_entity
    
    print("Setting up Map Configuration...")

    # -------------------------------------------------------------------------
    # 1. Create Projection if missing (Spherical Mercator)
    # -------------------------------------------------------------------------
    proj = db((ptable.epsg == 3857) | (ptable.name == "Spherical Mercator")).select().first()
    if not proj:
        print("Creating default projection (EPSG:3857)...")
        proj_id = ptable.insert(
            name = "Spherical Mercator",
            epsg = 3857,
            maxExtent = "-20037508.34,-20037508.34,20037508.34,20037508.34",
            proj4js = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs",
            units = "m"
        )
        db.commit()
        print(f"Created projection ID: {proj_id}")
    else:
        proj_id = proj.id
        print(f"Found existing projection ID: {proj_id}")

    # -------------------------------------------------------------------------
    # 2. Create GIS Config (Default Map Profile)
    # -------------------------------------------------------------------------
    # Check by UUID first (SITE_DEFAULT)
    config = db(ctable.uuid == "SITE_DEFAULT").select().first()
    
    if not config:
        # Check by name to avoid duplicates if UUID was wrong
        config = db(ctable.name == "Default Map Profile").select().first()
        
        if config:
            print(f"Found existing config by name: {config.name} (ID: {config.id}). Updating UUID...")
            db(ctable.id == config.id).update(uuid="SITE_DEFAULT", projection_id=proj_id)
            db.commit()
            config_id = config.id
        else:
            print("Creating Default Map Profile...")
            config_id = ctable.insert(
                name = "Default Map Profile",
                uuid = "SITE_DEFAULT",
                projection_id = proj_id,
                zoom = 2,
                lat = 0,
                lon = 0,
                pe_default = True,
                wmsbrowser_url = "https://ows.terrestris.de/osm/service?",
                wmsbrowser_name = "Web Map Service"
            )
            db.commit()
            print(f"Created GIS Config ID: {config_id}")
    else:
        config_id = config.id
        print(f"Found existing SITE_DEFAULT config ID: {config_id}")
        # Ensure projection and WMS are set
        if config.projection_id != proj_id or not config.wmsbrowser_url:
            db(ctable.id == config_id).update(
                projection_id=proj_id,
                wmsbrowser_url = "https://ows.terrestris.de/osm/service?",
                wmsbrowser_name = "Web Map Service"
            )
            db.commit()
            print("Updated config with Projection and WMS URL.")

    # -------------------------------------------------------------------------
    # 3. Create OpenStreetMap Layer
    # -------------------------------------------------------------------------
    osm_record = db(otable.name == "OpenStreetMap").select().first()
    
    if osm_record:
        print(f"Found OSM Record ID: {osm_record.id}")
        if not osm_record.layer_id:
            print("Creating missing gis_layer_entity for OSM...")
            layer_id = etable.insert(
                instance_type = "gis_layer_openstreetmap",
                name = "OpenStreetMap"
            )
            db(otable.id == osm_record.id).update(layer_id=layer_id)
            db.commit()
        else:
            layer_id = osm_record.layer_id
    else:
        print("Creating new OSM Layer and Entity...")
        layer_id = etable.insert(
            instance_type = "gis_layer_openstreetmap",
            name = "OpenStreetMap"
        )
        otable.insert(
            name = "OpenStreetMap",
            layer_id = layer_id,
            url1 = "http://a.tile.openstreetmap.org/",
            url2 = "http://b.tile.openstreetmap.org/",
            url3 = "http://c.tile.openstreetmap.org/",
            attribution = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
        )
        db.commit()
        print(f"Created OSM Layer ID: {layer_id}")

    # -------------------------------------------------------------------------
    # 4. Fix GIS Hierarchy (Ensure SITE_DEFAULT exists)
    # -------------------------------------------------------------------------
    print("Checking GIS Hierarchy...")
    htable = s3db.gis_hierarchy
    if db(htable.uuid == "SITE_DEFAULT").count() == 0:
        print("Creating SITE_DEFAULT in gis_hierarchy...")
        htable.insert(
            uuid="SITE_DEFAULT",
            L0="Country",
            L1="State / Province",
            L2="District",
            L3="City / Town / Village",
        )
        db.commit()
        print("Success: SITE_DEFAULT created in gis_hierarchy.")
    else:
        print("GIS Hierarchy SITE_DEFAULT already exists.")

    # -------------------------------------------------------------------------
    # 5. Fix OSM Layer
    # -------------------------------------------------------------------------
    link = db((ltable.config_id == config_id) & \
              (ltable.layer_id == layer_id)).select().first()
              
    if not link:
        print(f"Linking OSM Layer to Config...")
        ltable.insert(
            config_id = config_id,
            layer_id = layer_id,
            enabled = True,
            visible = True,
            base = True
        )
        db.commit()
        print("Link created successfully.")
    else:
        print("OSM Layer already linked.")
        if not link.enabled or not link.visible or not link.base:
            print("Updating link properties...")
            link.update_record(enabled=True, visible=True, base=True)
            db.commit()
            print("Link updated.")

    print("Map Setup Complete!")

except Exception as e:
    print(f"Error setting up map: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
