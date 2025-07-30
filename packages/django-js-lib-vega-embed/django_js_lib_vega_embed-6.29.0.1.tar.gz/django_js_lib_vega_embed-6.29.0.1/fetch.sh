##!/bin/bash
#set +ex
#
#VERSION="7.0.2"
#URL="https://registry.npmjs.org/vega-embed/-/vega-embed-${VERSION}.tgz"
#OUTPUT_ZIP="dist.tgz"
#curl -L -o $OUTPUT_ZIP $URL
#tar -xzf $OUTPUT_ZIP
#rm $OUTPUT_ZIP
#
#rm -dr js_lib_vega_embed/static/js_lib_vega_embed
#mv package/build js_lib_vega_embed/static/js_lib_vega_embed
#cp package/LICENSE LICENSE
#rm -r package
#git add js_lib_vega_embed/static/js_lib_vega_embed LICENSE
