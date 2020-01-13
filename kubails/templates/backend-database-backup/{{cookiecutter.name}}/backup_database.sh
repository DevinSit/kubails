set -e

DUMP_FILE="$NAMESPACE-database-backup-`date +%Y-%m-%d-%H-%M-%S`.dump"
echo "Creating dump: $DUMP_FILE"

pg_dump -w --blobs > $DUMP_FILE

if [ $? -ne 0 ]; then
    rm $DUMP_FILE
    echo "Back up not created; check db connection settings"
    exit 1
fi

# $BACKUP_BUCKET and $NAMESPACE are provided as environment variables by the cronjob resource
gsutil mv $DUMP_FILE "gs://$BACKUP_BUCKET/$NAMESPACE/"

echo "Successfully backed up"
exit 0
