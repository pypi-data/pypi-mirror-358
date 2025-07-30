set -ex

mkdir -p _downloads

curl -L -o _downloads/vega5.js https://cdn.jsdelivr.net/npm/vega@5
curl -L -o _downloads/vega-lite5.js https://cdn.jsdelivr.net/npm/vega-lite@5
curl -L -o _downloads/vega-embed6.js https://cdn.jsdelivr.net/npm/vega-embed@6

cp _downloads/vega5.js _downloads/vega-lite5.js _downloads/vega-embed6.js  ./js_lib_vega_embed/static/js_lib_vega_embed
cat _downloads/vega5.js _downloads/vega-lite5.js _downloads/vega-embed6.js  > ./js_lib_vega_embed/static/js_lib_vega_embed/vega-embed-full.js

git add -v ./js_lib_vega_embed/static/js_lib_vega_embed/
