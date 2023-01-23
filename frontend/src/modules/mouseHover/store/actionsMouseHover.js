import {createGfiFeature} from "../../../api/gfi/getWmsFeaturesByMimeType";
import {buffer} from "ol/extent";
import Point from "ol/geom/Point";

export default {
    /**
     * Sets the config-params of this MouseHover into state.
     * Adds the overlay and eventListener for the map.
     * @returns {void}
     */
    initialize ({state, commit, dispatch}) {
        const {numFeaturesToShow, infoText} = Config.mouseHover,
            map = mapCollection.getMap("2D");
        let featuresAtPixel = [];

        commit("setMouseHoverLayers");
        commit("setMouseHoverInfos");
        map.addOverlay(state.overlay);

        if (numFeaturesToShow) {
            commit("setNumFeaturesToShow", numFeaturesToShow);
        }
        if (infoText) {
            commit("setInfoText", infoText);
        }
        map.on("pointermove", (evt) => {
            if (!state.isActive || evt.originalEvent.pointerType === "touch") {
                return;
            }
            featuresAtPixel = [];
            commit("setHoverPosition", evt.coordinate);

            // works for WebGL layers that are point layers
            // behavior is different from GFI, reason unclear, same method
            map.forEachFeatureAtPixel(evt.pixel, (feature, layer) => {
                if (layer?.getVisible()) {
                    if (feature.getProperties().features) {
                        feature.get("features").forEach(clusteredFeature => {
                            featuresAtPixel.push(createGfiFeature(
                                layer,
                                "",
                                clusteredFeature
                            ));
                        });
                    }
                    else {
                        featuresAtPixel.push(createGfiFeature(
                            layer,
                            "",
                            feature
                        ));
                    }
                }
            });
            /** check WebGL Layers
             * use buffered coord instead of pixel for hitTolerance
             * only necessary for WebGL polygon and line layers
             * @todo refactor?
            */
            map.getLayers().getArray()
                .filter(layer => layer.get("typ") === "WebGL" && !layer.get("isPointLayer")) // point features are already caught by map.forEachFeatureAtPixel loop
                .forEach(layer => {
                    if (layer.get("gfiAttributes") && layer.get("gfiAttributes") !== "ignore") {
                        /**
                         * use OL resolution based buffer to adjust the hitTolerance (in m) for lower zoom levels
                         */
                        const hitBox = buffer(
                            new Point(evt.coordinate).getExtent(),
                            (layer.get("hitTolerance") || 1) * Math.sqrt(mapCollection.getMapView("2D").getResolution())
                        );

                        layer.getSource()?.forEachFeatureIntersectingExtent(hitBox, feature => {
                            featuresAtPixel.push(createGfiFeature(
                                layer,
                                "",
                                feature
                            ));
                        });
                    }
                });
            state.overlay.setPosition(evt.coordinate);
            state.overlay.setElement(document.querySelector("#mousehover-overlay"));
            commit("setInfoBox", null);

            if (featuresAtPixel.length > 0) {
                dispatch("filterInfos", featuresAtPixel);
            }
        });
    },

    /**
     * Filters the infos from each feature that should be displayed.
     * @param {Array} features array of hovered Features
     * @returns {void}
     */
    filterInfos ({state, commit}, features) {
        const infoBox = [];

        if (features.length > 0) {
            features.forEach(feature => {
                const configInfosForFeature = state.mouseHoverInfos.find(info => info.id === feature.getLayerId());

                if (configInfosForFeature) {
                    const featureProperties = feature.getProperties(),
                        featureInfos = typeof configInfosForFeature.mouseHoverField === "string" ? configInfosForFeature.mouseHoverField : configInfosForFeature.mouseHoverField.filter(key => Object.keys(featureProperties).includes(key)),
                        featureDetails = [];

                    if (Array.isArray(featureInfos)) {
                        featureInfos.forEach(info => {
                            featureDetails.push(featureProperties[info]);
                        });
                    }
                    else {
                        featureDetails.push(featureProperties[featureInfos]);
                    }
                    infoBox.push(featureDetails);
                    commit("setPleaseZoom", features.length > state.numFeaturesToShow);
                    commit("setInfoBox", infoBox.slice(0, state.numFeaturesToShow));
                }
            });
        }
    }
};
