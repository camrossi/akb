#!/bin/bash 
export AWS_PAGER=""

KEY=$(basename $1)
#Calculate MD5 for upload
MD5=$(openssl md5 -binary $1 | base64)

#Split
split -b 4096m $1 $1.part-

# Create MultiPart Upload
UPLOAD_ID=$(aws s3api create-multipart-upload \
    --bucket $2 \
    --key $KEY \
    --metadata md5=$MD5 | jq -r .UploadId)

C=1
for PART in `/bin/ls $1.part-*`
    do
        aws s3api upload-part \
            --bucket $2 \
            --key $KEY \
            --part-number $C \
            --body $PART \
            --upload-id $UPLOAD_ID 
        C=$((C+1))
    done

aws s3api list-parts \
    --bucket $2 \
    --key $KEY \
    --upload-id $UPLOAD_ID | jq '.Parts[] |={PartNumber,ETag} | {Parts: .Parts}' > /tmp/part.json

aws s3api complete-multipart-upload \
    --multipart-upload file:///tmp/part.json \
    --bucket $2 \
    --key $KEY \
    --upload-id $UPLOAD_ID