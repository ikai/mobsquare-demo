    // Simple JavaScript Templating
    // John Resig - http://ejohn.org/ - MIT Licensed
    // Blog post - http://ejohn.org/blog/javascript-micro-templating/
    (function(){
      var cache = {};

      this.tmpl = function tmpl(str, data){
        // Figure out if we're getting a template, or if we need to
        // load the template - and be sure to cache the result.
        var fn = !/\W/.test(str) ?
          cache[str] = cache[str] ||
            tmpl(document.getElementById(str).innerHTML) :

          // Generate a reusable function that will serve as a template
          // generator (and which will be cached).
          new Function("obj",
            "var p=[],print=function(){p.push.apply(p,arguments);};" +

            // Introduce the data as local variables using with(){}
            "with(obj){p.push('" +

            // Convert the template into pure JavaScript
            str
              .replace(/[\r\t\n]/g, " ")
              .split("<%").join("\t")
              .replace(/((^|%>)[^\t]*)'/g, "$1\r")
              .replace(/\t=(.*?)%>/g, "',$1,'")
              .split("\t").join("');")
              .split("%>").join("p.push('")
              .split("\r").join("\\'")
          + "');}return p.join('');");

        // Provide some basic currying to the user
        return data ? fn( data ) : fn;
      };
    })();

    var main = {};
    /*
        Gets the location of the user. Access a callback(lat, long) to be invoked
        when we have the information.
        @param {function} callback(lat, long) to be invoked when information is available
    */
    main.getLocation = function(callback) {
        var wrappedCallback = function(position) {
            main._onGetLocation(position, callback)
        } 
        navigator.geolocation.getCurrentPosition(wrappedCallback);
    }
    
    /**
        Uses the lat/long provided by geolocation API to fetch
        the nearby places (Facebook API) along with any additional
        annotations.
    */
    main.loadNearbyLocations = function() {
        main.getLocation(function(lat, lon) {
            console.log(lat)
            console.log(lon);
            main.lat = lat;
            main.lon = lon;
            $.getJSON("/nearby?lat=" + lat + "&lon=" + lon, main.onLoadNearbyLocations)
        });
    }
    
    /**
        Callback for 
    */
    main.onLoadNearbyLocations = function(json) {
        console.log(json);
        $.each(json.data, function(i, location) {
            $("#locations").append(tmpl("location_row_tmpl", 
                {   "id"        : location["id"], 
                    "i"         : i,
                    "name"      : location["name"],
                    "city"      : location["location"]["city"],
                    "country"   : location["location"]["country"], 
                    "category"  : location["category"] }));
        });
    }
    
    /**
        Private callback that is wrapped when we get back our data.
    */
    main._onGetLocation = function(position, callback) {
        var lat = position.coords.latitude;
        var lon = position.coords.longitude;
        callback(lat, lon);
    }
    
    $(function() {
        main.loadNearbyLocations(); 
    });
