import os
import sys

import web


def migrate(db, directory):
    try:
        db.where("schema_info")
    except:
        db.query("create table schema_info (version int not null)")

    sys.path.append(directory)
    for migration in sorted_migrations(os.listdir(directory)):
        if db.where("schema_info", version=migration.version):
            print "Skipping %s since it's already applied." % migration
            continue
        print "Applying %s" % migration
        __import__(migration.name).up(db)
        db.insert("schema_info", version=migration.version)


def sorted_migrations(fnames):
    def build_migration(fname):
        name = os.path.splitext(fname)[0]
        version = int(name.split("_")[-1])
        return web.storage(fname=fname, name=name, version=version)

    migrations = [build_migration(f) for f in fnames if f.endswith('.py')]
    return sorted(migrations, key=lambda m: m.version)


if __name__ == "__main__":
    import config
    migrate(config.dbn, "config/migrations")
