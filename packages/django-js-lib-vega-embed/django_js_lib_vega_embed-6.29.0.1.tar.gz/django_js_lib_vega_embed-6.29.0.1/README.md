# Vega Embed for Django

[Vega Embed](https://github.com/vega/vega-embed) packaged in a Django reusable app.

This package includes the original JS and CSS files from vega, vega-lite and vega-embed.

- Vega: 5.33.0
- Vega Lite: 5.23.0
- Vega Embed: 6.29.0


## Installation

    pip install django-js-lib-vega-embed

## Usage

1. Add `"js_lib_vega_embed"` to your `INSTALLED_APPS` setting like this::

       INSTALLED_APPS = [
           ...
           "js_lib_vega_embed",
           ...
       ]

2. In your template use:
   
       {% load static %}
   
   ...
   
       <script src="{%static "js_lib_vega_embed/vega-embed-full.js" %}"></script>

   or:

       <script src="{%static "js_lib_vega_embed/vega5.js" %}"></script>
       <script src="{%static "js_lib_vega_embed/vega-lite5.js" %}"></script>
       <script src="{%static "js_lib_vega_embed/vega-embed6.js" %}"></script>
