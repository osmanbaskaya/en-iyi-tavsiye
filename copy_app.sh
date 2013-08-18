rm -rf $2
cp -r $1 $2
mv $2/templates/$1 $2/templates/$2
ln -s /data/imdbdata_images/item-imgs $2/static/
