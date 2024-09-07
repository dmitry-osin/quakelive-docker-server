#! /bin/bash
# autodownload.sh - quake live dedicated server workshop item download utility.
# created by Thomas Jones on 03/10/15.
# modified by Dmitry Osin on 06/09/24.
# thomas@tomtecsolutions.com

echo "========== AutoDownload.sh has started. =========="
echo "========= $(date) ========="

workshopIDs=`cat /root/Steam/steamapps/common/qlds/baseq3/workshop.txt | grep -v '#' | sed '/^[ \t]*$/d'`
numOfIDs=`echo "$workshopIDs" | wc -l`
counter=0
while [ $counter -lt $numOfIDs ]; do
	currentID=`echo $workshopIDs | awk '{ print $1 }'`
	workshopIDs=`echo $workshopIDs | cut -d ' ' -f2-`
	echo -e "Downloading item $currentID from Steam... ($(expr $counter + 1)/$numOfIDs)"
	/root/Steam/steamcmd.sh +login anonymous +workshop_download_item 282440 $currentID +quit > /dev/null
	((counter++))
done
echo "Removing old workshop data and moving new items into place..."
rm -r /root/Steam/steamapps/common/qlds/steamapps/workshop

mv /root/Steam/steamapps/workshop /root/Steam/steamapps/common/qlds/steamapps/workshop
echo Done.
exit 0
