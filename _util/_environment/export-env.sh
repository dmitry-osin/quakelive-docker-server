#!/bin/bash
filename='server.env'

echo "# Begin QuakeLive server variables" >> /etc/environment
while read p; do
    echo "export $p" >> /etc/environment
done < "$filename"
echo "# End QuakeLive server variables" >> /etc/environment

. /etc/environment