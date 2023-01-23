import Layer from "./layer";
import WFSLayer from "./wfs";
import {geojson, wfs} from "@masterportal/masterportalapi";
import rawLayerList from "@masterportal/masterportalapi/src/rawLayerList";
import WebGLPointsLayer from "ol/layer/WebGLPoints";
import WebGLVectorLayerRenderer from "ol/renderer/webgl/VectorLayer";
import VectorLayer from "ol/layer/Layer";
import LoaderOverlay from "../../utils/loaderOverlay";
import VectorSource from "ol/source/Vector.js";
import * as bridge from "./RadioBridge.js";
import {bbox, all} from "ol/loadingstrategy.js";
import {packColor} from "ol/renderer/webgl/shaders";
import {getCenter} from "ol/extent";

/**
 * The default style for OpenLayers WebGLPoints class
 * @see https://openlayers.org/en/latest/examples/webgl-points-layer.html
 * @private
 */
const defaultStyle = {
    symbol: {
        symbolType: "circle",
        size: 20,
        color: "#006688",
        rotateWithView: false,
        offset: [0, 0],
        opacity: 0.6
    }
};

/**
 * Creates a layer of type WebGL
 * Uses different render pipelines for point geometries vs. linestring/polygon geometries
 * @augments Layer
 * @class
 * @param {Object} attrs  attributes of the layer
 * @property {module:ol/Feature[]} features the OL features
 * @property {module:ol/source/Vector} source the OL source object
 * @property {module:ol/layer/Layer} layer the OL layer object
 * @property {Boolean} _isPointLayer (private) whether the layer consists only of points
 * @returns {void}
 */
export default function WebGLLayer (attrs) {
    const defaults = {
            style: defaultStyle,
            hitTolerance: 10,
            sourceUpdated: false // necessary if source layer is WFS
        },
        // use referenced source layer or local layer if sourceId is layerType ("GeoJson", "WFS")
        sourceLayer = rawLayerList.getLayerWhere({id: attrs.sourceId}) || {...attrs, typ: attrs.sourceId};

    this.features = [];
    this.createLayer({...defaults, ...attrs}, sourceLayer);

    Layer.call(this, {...sourceLayer, ...defaults, ...attrs}, this.layer, !attrs.isChildLayer);
    this.createLegend(attrs, sourceLayer);
}

// Link prototypes and add prototype methods, means WFSLayer uses all methods and properties of Layer
WebGLLayer.prototype = Object.create(Layer.prototype);

/**
 * Triggert by Layer to create a ol/layer/Vector
 * Sets all needed attributes at the layer and the layer source.
 * Based on WFSLayer.createLayer
 * @memberof WebGLLayer
 * @override
 * @param {Object} attrs  attributes of the layer
 * @fires MapView#RadioRequestGetProjection
 * @returns {void}
 */
WebGLLayer.prototype.createLayer = function (attrs, sourceLayer) {
    const options = {
        map: mapCollection.getMap("2D"),
        featuresFilter: this.getFeaturesFilterFunction(attrs),
        beforeLoading: function () {
            if (this.get("isSelected") || attrs.isSelected) {
                LoaderOverlay.show();
            }
        }.bind(this),
        afterLoading: function (features) {
            this.afterLoading(features, attrs);
        }.bind(this),
        onLoadingError: (error) => {
            console.error("masterportal wfs loading error:", error);
        },
        wfsFilter: sourceLayer.wfsFilter,
        loadingParams: {
            xhrParameters: sourceLayer.isSecured ? {credentials: "include"} : undefined,
            propertyname: WFSLayer.prototype.getPropertyname(sourceLayer) || undefined,
            // only used if loading strategy is all
            bbox: attrs.bboxGeometry ? attrs.bboxGeometry.getExtent().toString() : undefined
        },
        loadingStrategy: attrs.loadingStrategy === "all" ? all : bbox
    };

    this.source = this.createLayerSource(sourceLayer, options);
    this.layer = this.createLayerInstance({...sourceLayer, ...attrs});
};

/**
 * Returns a function to filter features with.
 * @memberof WebGLLayer
 * @param {Object} attrs params of the raw layer
 * @returns {Function} to filter features with
 */
WebGLLayer.prototype.getFeaturesFilterFunction = function (attrs) {
    return function (features) {
        // only use features with a geometry
        let filteredFeatures = features.filter(feature => feature.getGeometry() !== undefined);

        if (attrs.bboxGeometry) {
            filteredFeatures = filteredFeatures.filter((feature) => attrs.bboxGeometry.intersectsCoordinate(getCenter(feature.getGeometry().getExtent())));
        }
        return filteredFeatures;
    };
};

/**
 * Creates a layer object to extend from.
 * @memberof WebGLLayer
 * @augments VectorLayer
 * @implements {WebGLVectorLayerRenderer}
 * @param {Object} attrs attributes of the layer
 * @returns {module:ol/layer/Layer} the LocalWebGLLayer with a custom renderer for WebGL styling
 */
WebGLLayer.prototype.createVectorLayerRenderer = function () {
    /**
     * @class LocalWebGLLayer
     * @see https://openlayers.org/en/latest/examples/webgl-vector-layer.html
     * @description the temporary class with a custom renderer to render the vector data with WebGL
     */
    class LocalWebGLLayer extends VectorLayer {
        /**
         * Creates a new renderer that takes the defined style of the new layer as an input
         * @returns {module:ol/renderer/webgl/WebGLVectorLayerRenderer} the custom renderer
         * @experimental
         */
        createRenderer () {
            return new WebGLVectorLayerRenderer(this, WebGLLayer.prototype.getRenderFunctions());
        }
    }

    return LocalWebGLLayer;
};

/**
 * Creates a VectorSource. Either from WFS or GeoJSON.
 * @memberof WebGLLayer
 * @param {Object} rawLayer layer specification as in services.json
 * @param {Object} options - options of the target layer
 * @returns {module:ol/source/Vector} returns the VectorSource
 */
WebGLLayer.prototype.createLayerSource = function (rawLayer, options) {
    /** create layer source with WFS loader, if source layer is WFS
     * @external masterportalapi
     */
    if (rawLayer.typ === "WFS") {
        const wfsSource = wfs.createLayerSource(rawLayer, options);

        // clean the old data if WFS is reloaded, or BBOX loading strategy is used
        wfsSource.on("featuresloadstart", this.clearSource.bind(this));
        return wfsSource;
    }

    /** create layer source with GeoJSON loader, if source layer is GeoJSON
     *  @external masterportalapi
     */
    if (rawLayer.typ === "GeoJSON") {
        return geojson.createLayerSource({url: rawLayer.url, features: rawLayer.features}, options);
    }

    return new VectorSource({features: rawLayer.features}); // else return VectorSource, potentially with features
};

/**
 * Creates the OL Layer instance, used to rebuild the layer when shown again after layer has been disposed
 * @memberof WebGLLayer
 * @param {Object} attrs - the attributes of the layer
 * @returns {module:ol/layer/Vector} returns the layer instance
 */
WebGLLayer.prototype.createLayerInstance = function (attrs) {
    let LayerConstructor = WebGLPointsLayer;
    const opts = {
        id: attrs.id,
        source: this.source,
        disableHitDetection: false,
        name: attrs.name,
        typ: attrs.typ,
        gfiAttributes: attrs.gfiAttributes,
        gfiTheme: attrs.gfiTheme,
        hitTolerance: attrs.hitTolerance,
        opacity: attrs.transparency ? (100 - attrs.transparency) / 100 : attrs.opacity
    };

    /** @see https://openlayers.org/en/latest/examples/webgl-points-layer.html */
    if (this.isPointLayer(attrs.isPointLayer)) {
        /**
         * @deprecated
         * @todo will be replaced in the next OL release and incorporated in the WebGLVectorLayerRenderer
         */
        return new LayerConstructor({
            style: attrs.style,
            disableHitDetection: false,
            ...opts,
            isPointLayer: this._isPointLayer
        });
    }

    // use ol/renderer/webgl/WebGLVectorLayerRenderer if not point layer
    LayerConstructor = this.createVectorLayerRenderer(attrs);
    return new LayerConstructor({
        ...opts,
        isPointLayer: this._isPointLayer
    });
};

/**
 * Creates the legend
 * @override
 * @memberof WebGLLayer
 * @param {Object} attrs  attributes of the layer
 * @returns {void}
 */
WebGLLayer.prototype.createLegend = function (attrs, sourceLayer) {
    const
        styleId = attrs.styleId || sourceLayer?.styleId,
        legendURL = this.get("legendURL") || sourceLayer?.legendURL,
        styleModel = bridge.getStyleModelById(styleId);
    let
        legend = this.get("legend");

    /**
     * @deprecated in 3.0.0
     */
    if (legendURL) {
        if (legendURL === "") {
            legend = true;
        }
        else if (legendURL === "ignore") {
            legend = false;
        }
        else {
            legend = legendURL;
        }
    }

    if (Array.isArray(legend)) {
        this.setLegend(legend);
    }
    else if (styleModel && legend === true) {
        // run styleModel functions for WFS source
        if (sourceLayer.typ === "WFS") {
            if (!sourceLayer.isSecured) {
                styleModel.getGeometryTypeFromWFS(
                    sourceLayer.url,
                    sourceLayer.version,
                    sourceLayer.featureType,
                    sourceLayer.styleGeometryType,
                    sourceLayer.useProxy
                );
            }
            else if (sourceLayer.isSecured) {
                styleModel.getGeometryTypeFromSecuredWFS(
                    sourceLayer.url,
                    sourceLayer.version,
                    sourceLayer.featureType,
                    sourceLayer.styleGeometryType
                );
            }
        }
        this.setLegend(styleModel.getLegendInfos());
    }
    else if (typeof legend === "string") {
        this.setLegend([legend]);
    }
};

/**
 * Updates the layers source by calling refresh at source.
 * @override
 * @implements {WFSLayer.updateSource}
 * @memberof WebGLLayer
 * @returns {void}
 */
WebGLLayer.prototype.updateSource = function () {
    WFSLayer.prototype.updateSource.call(this);
};

/**
 * Clears the layer' source.
 * @memberof WebGLLayer
 * @returns {void}
 */
WebGLLayer.prototype.clearSource = function () {
    this.source.clear();
};

/**
 * Parses the vectorStyle from style.json to the feature
 * to reduce processing on runtime
 * @memberof WebGLLayer
 * @private
 * @param {module:ol/Feature} feature - the feature to check
 * @param {module:Backbone/Model} [styleModel] - (optional) the style model from StyleList
 * @returns {void}
 */
WebGLLayer.prototype.formatFeatureStyles = function (feature, styleModel) {
    // extract first matching rule only
    const rule = styleModel?.getRulesForFeature(feature)[0];

    // don't set on properties to avoid GFI issues
    // undefined if no match
    feature._styleRule = rule;
};

/**
 * Layouts the geometry coordinates, removes the Z component
 * @deprecated Will be removed in release
 * @memberof WebGLLayer
 * @private
 * @param {module:ol/Feature} feature - the feature to format
 * @returns {void}
 */
WebGLLayer.prototype.formatFeatureGeometry = function (feature) {
    feature.getGeometry()?.setCoordinates?.(feature.getGeometry().getCoordinates(), "XY");
};

/**
 * Cleans the data by automatically parsing data provided as strings to the accurate data type
 * @todo Extend to Date types
 * @memberof WebGLLayer
 * @private
 * @param {module:ol/Feature} feature - the feature to format
 * @param {Array<String>} [excludeTypes=["boolean"]] - types that should not be parsed from strings
 * @returns {void}
 */
WebGLLayer.prototype.formatFeatureData = function (feature, excludeTypes = ["boolean"]) {
    for (const key in feature.getProperties()) {
        const
            valueAsNumber = parseFloat(feature.get(key)),
            valueIsTrue = typeof feature.get(key) === "string" && feature.get(key).toLowerCase() === "true" ? true : undefined,
            valueIsFalse = typeof feature.get(key) === "string" && feature.get(key).toLowerCase() === "false" ? false : undefined;

        if (!isNaN(parseFloat(feature.get(key))) && !excludeTypes.includes("number")) {
            feature.set(key, valueAsNumber);
        }
        if (valueIsTrue === true && !excludeTypes.includes("boolean")) {
            feature.set(key, valueIsTrue);
        }
        if (valueIsFalse === false && !excludeTypes.includes("boolean")) {
            feature.set(key, valueIsFalse);
        }
    }
};

/**
 * parses the styling rules for the renderer
 * @static
 * @private
 * @returns {Object} the style options object with conditional functions
 */
WebGLLayer.prototype.getRenderFunctions = function () {
    return {
        /**
         * Used for polygon fills
         * Reads the relevant properties from the Masterportal style object
         * @see https://bitbucket.org/geowerkstatt-hamburg/masterportal/src/dev/doc/style.json.md
         */
        fill: {
            attributes: {
                color: (feature) => {
                    if (!feature._styleRule) {
                        return packColor("#006688");
                    }
                    return packColor(feature._styleRule.style.polygonFillColor);
                },
                opacity: (feature) => {
                    if (!feature._styleRule) {
                        return 0.8;
                    }
                    return typeof feature._styleRule.style.polygonFillColor[3] === "number" ?
                        feature._styleRule.style.polygonFillColor[3] : 1;
                }
            }
        },
        stroke: {
            /**
             * Used for polygon edges and lineStrings
             * Reads the relevant properties from the Masterportal style object
             * @see https://bitbucket.org/geowerkstatt-hamburg/masterportal/src/dev/doc/style.json.md
             */
            attributes: {
                color: (feature) => {
                    if (!feature._styleRule) {
                        return packColor("#006688");
                    }
                    return packColor(feature._styleRule.style.polygonStrokeColor);
                },
                width: (feature) => {
                    if (!feature._styleRule) {
                        return 1;
                    }
                    return feature._styleRule.style.polygonStrokeWidth;
                },
                opacity: (feature) => {
                    if (!feature._styleRule) {
                        return 1;
                    }
                    return typeof feature._styleRule.style.polygonStrokeColor[3] === "number" ?
                        feature._styleRule.style.polygonStrokeColor[3] : 1;
                }
            }
        },
        point: {
            /**
             * As of now, the generic VectorLayerRenderer only supports points rendered as quads
             * available attributes: color, size, opacity
             * Due to that, we use WebGLPoints Layer Class for point geom types
             * Reads the relevant properties from the Masterportal style object
             * @see https://bitbucket.org/geowerkstatt-hamburg/masterportal/src/dev/doc/style.json.md
             */
            attributes: {
                color: (feature) => {
                    if (!feature._styleRule) {
                        return packColor("#006688");
                    }
                    return packColor(feature._styleRule.style.circleFillColor);
                },
                size: (feature) => {
                    if (!feature._styleRule) {
                        return 20;
                    }
                    return feature._styleRule.style.circleRadius;
                },
                opacity: (feature) => {
                    if (!feature._styleRule) {
                        return 0.8;
                    }
                    return typeof feature._styleRule.style.circleFillColor[3] === "number" ?
                        feature._styleRule.style.circleFillColor[3] : 1;
                }
            }
        }
    };
};

/**
 * Sets the attribute isSelected and sets the layers visibility. If newValue is false, the layer is removed from map.
 * Calls the layer super, disposes WebGL resources if layer is set invisible
 * @override
 * @memberof WebGLLayer
 * @implements {Layer.setIsSelected}
 * @param {Boolean} newValue true, if layer is selected
 * @todo rerender map after canvas render complete
 *       necessary for GPU rendering, since no map/layer event catches the rendering correctly
 *       otherwise icons will be rendered as black quads
 * @returns {void}
 */
WebGLLayer.prototype.setIsSelected = async function (newValue) {
    if (this.isDisposed()) {
        // recreate layer instance if buffer has been disposed
        this.layer = this.createLayerInstance(this.attributes);
    }

    Layer.prototype.setIsSelected.call(this, newValue);

    if (!this.get("isVisibleInMap")) {
        // dispose WebGL buffer if layer removed
        this.layer.dispose();
    }
};

/**
 * Hides all features by removing them from the layer source.
 * @memberof WebGLLayer
 * @returns {void}
 */
WebGLLayer.prototype.hideAllFeatures = function () {
    this.clearSource();
};

/**
 * sets the layerSource to have the inital features array
 * @memberof WebGLLayer
 * @returns {void}
 */
WebGLLayer.prototype.showAllFeatures = function () {
    this.hideAllFeatures();
    this.source.addFeatures(this.features);
};

/**
 * Filters the visibility of features by ids.
 * @memberof WebGLLayer
 * @param  {String[]} featureIdList Feature ids to be shown.
 * @return {void}
 */
WebGLLayer.prototype.showFeaturesByIds = function (featureIdList) {
    const featuresToShow = featureIdList.map(id => this.features.find(feature => feature.getId() === id));

    this.hideAllFeatures();
    this.source.addFeatures(featuresToShow);
};

/**
 * Returns whether the WebGL resources have been disposed
 * @memberof WebGLLayer
 * @public
 * @readonly
 * @returns {Boolean} true / false
 */
WebGLLayer.prototype.isDisposed = function () {
    return this.layer ? this.layer.disposed : true;
};

/**
 * Returns whether the layer consists only of points
 * @deprecated Will be removed as soon as OL WebGL features are consolidated
 * @memberof WebGLLayer
 * @public
 * @readonly
 * @param {Boolean} [isPointLayer] boolean flag set in config/service
 * @returns {Boolean} true / false
 */
WebGLLayer.prototype.isPointLayer = function (isPointLayer) {
    if (this._isPointLayer === undefined) {
        // if provided, set flag hard
        if (typeof isPointLayer === "boolean") {
            this._isPointLayer = isPointLayer;
        }
        else {
            this._isPointLayer = this.source.getFeatures().every(feature => {
                const geomType = feature.getGeometry()?.getType();

                return geomType === "Point" || geomType === "MultiPoint";
            });
        }
    }

    return this._isPointLayer;
};

/**
 * feature transformations called after loading
 * called by the layer source loader, binds the instance of the layer model
 * should be called on each source refresh
 * @param {module:ol/Feature[]} features - the features list
 * @param {object} attrs - the layers attributes object
 * @returns {void}
 */
WebGLLayer.prototype.afterLoading = function (features, attrs) {
    const styleModel = bridge.getStyleModelById(attrs.styleId); // load styleModel to extract rules per feature

    if (Array.isArray(features)) {
        features.forEach((feature, idx) => {
            if (typeof feature?.getId === "function" && typeof feature.getId() === "undefined") {
                feature.setId("webgl-" + attrs.id + "-feature-id-" + idx);
            }
            this.formatFeatureGeometry(feature); /** @deprecated will propbably not be necessary anymore in release version */
            this.formatFeatureStyles(feature, styleModel); /** @todo needs refactoring for production  */
            this.formatFeatureData(feature, attrs.excludeTypesFromParsing);
        });
    }
    this.featuresLoaded(attrs.id, features);
    this.features = features;
    if (this.get("isSelected") || attrs.isSelected) {
        LoaderOverlay.hide();
    }
};
