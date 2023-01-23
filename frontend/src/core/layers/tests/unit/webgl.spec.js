import VectorSource from "ol/source/Vector.js";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import Polygon from "ol/geom/Polygon";
import {WFS, GeoJSON} from "ol/format.js";
import {expect} from "chai";
import sinon from "sinon";
import BaseLayer from "../../layer";
import WebGLLayer from "../../webgl";
import WebGLPointsLayer from "ol/layer/WebGLPoints";
import Layer from "ol/layer/Layer";
import store from "../../../../app-store";
import rawLayerList from "@masterportal/masterportalapi/src/rawLayerList";
import {packColor} from "ol/renderer/webgl/shaders";

describe("src/core/layers/webgl.js", () => {
    const consoleWarn = console.warn;
    let layerAttrs, sourceLayerAttrs;

    before(() => {
        mapCollection.clear();
        const map = {
            id: "ol",
            mode: "2D",
            addInteraction: sinon.stub(),
            removeInteraction: sinon.stub(),
            addLayer: () => sinon.stub(),
            getView: () => ({
                getResolutions: () => [2000, 1000]
            }),
            getLayers: () => ({
                forEach: sinon.stub(),
                getArray: () => []
            })
        };

        mapCollection.addMap(map, "2D");
        i18next.init({
            lng: "cimode",
            debug: false
        });
    });
    beforeEach(() => {
        layerAttrs = {
            name: "webglTestLayer",
            id: "id",
            typ: "WebGL",
            sourceId: "sourceId"
        };
        sourceLayerAttrs = {
            url: "https://url.de",
            name: "wfsSourceLayer",
            id: "sourceId",
            typ: "WFS",
            version: "2.0.0",
            gfiTheme: "gfiTheme",
            isChildLayer: false,
            transparent: false,
            isSelected: false,
            featureNS: "http://www.deegree.org/app",
            featureType: "krankenhaeuser_hh"
        };
        store.getters = {
            treeType: "custom"
        };
        console.warn = sinon.stub();
        sinon.stub(rawLayerList, "getLayerWhere").callsFake((attrs) => {
            if (attrs.id === "sourceId") {
                return sourceLayerAttrs;
            }
            return undefined;
        });
    });

    afterEach(() => {
        sinon.restore();
        console.warn = consoleWarn;
    });

    describe("createLayer", () => {
        it("should create a layer with source and features property", function () {
            const webglLayer = new WebGLLayer(layerAttrs),
                layer = webglLayer.get("layer"),
                source = webglLayer.source,
                features = webglLayer.features;

            expect(layer).to.be.an.instanceof(Layer);
            expect(layer.getSource()).to.equal(source);
            expect(layer.getSource()).to.be.an.instanceof(VectorSource);
            expect(features).to.be.an.instanceof(Array);
            expect(layer.get("id")).to.be.equals(layerAttrs.id);
            expect(layer.get("name")).to.be.equals(layerAttrs.name);
            expect(layer.get("gfiTheme")).to.be.equals(sourceLayerAttrs.gfiTheme);
        });
        it("should set layer visible when isSelected=true", function () {
            layerAttrs.isSelected = true;
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.get("isVisibleInMap")).to.be.true;
            expect(webglLayer.get("layer").getVisible()).to.be.true;
        });
        it("should set layer visible when isSelected=false", function () {
            layerAttrs.isSelected = false;
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.get("isVisibleInMap")).to.be.false;
            expect(webglLayer.get("layer").getVisible()).to.be.false;
        });
    });
    describe("createLayerSource", () => {
        it("should create a source with WFS format", () => {
            const
                createLayerSource = sinon.spy(WebGLLayer.prototype, "createLayerSource"),
                webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.source.getFormat()).to.be.an.instanceof(WFS);
            expect(createLayerSource.calledOnce).to.be.true;
        });
        it("should create a source with GeoJSON format", () => {
            sourceLayerAttrs.typ = "GeoJSON";
            const
                createLayerSource = sinon.spy(WebGLLayer.prototype, "createLayerSource"),
                webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.source.getFormat()).to.be.an.instanceof(GeoJSON);
            expect(createLayerSource.calledOnce).to.be.true;
        });
        it("should create a source without format, but with features", () => {
            layerAttrs.sourceId = undefined;
            layerAttrs.features = [new Feature()];
            const
                createLayerSource = sinon.spy(WebGLLayer.prototype, "createLayerSource"),
                webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.source.getFormat()).to.be.undefined;
            expect(webglLayer.source.getFeatures()).to.have.lengthOf(1);
            expect(createLayerSource.calledOnce).to.be.true;
        });
    });
    describe("createLayerInstance", () => {
        it("should return a WebGLPointsLayer", () => {
            layerAttrs.isPointLayer = true;
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.layer).to.be.instanceof(WebGLPointsLayer);
            expect(webglLayer.layer.get("isPointLayer")).to.equal(true);
            expect(webglLayer._isPointLayer).to.equal(true);
        });
        it("should return a custom Layer", () => {
            layerAttrs.isPointLayer = false;
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.layer).to.be.instanceof(Layer);
            expect(webglLayer.layer).to.not.be.instanceof(WebGLPointsLayer);
            expect(webglLayer.layer.get("isPointLayer")).to.equal(false);
            expect(webglLayer._isPointLayer).to.equal(false);
        });
        it("should return a WebGLPointsLayer, based on features", () => {
            layerAttrs.sourceId = undefined;
            layerAttrs.features = [new Feature({geometry: new Point([0, 0])})];
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.layer).to.be.instanceof(WebGLPointsLayer);
            expect(webglLayer.layer.get("isPointLayer")).to.equal(true);
            expect(webglLayer._isPointLayer).to.equal(true);
        });
        it("should return a custom Layer, based on features", () => {
            layerAttrs.sourceId = undefined;
            layerAttrs.features = [new Feature({geometry: new Polygon([[[0, 0], [1, 0], [0, 1], [0, 0]]])})];
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.layer).to.be.instanceof(Layer);
            expect(webglLayer.layer).to.not.be.instanceof(WebGLPointsLayer);
            expect(webglLayer.layer.get("isPointLayer")).to.equal(false);
            expect(webglLayer._isPointLayer).to.equal(false);
        });
    });
    describe("getFeaturesFilterFunction", () => {
        it("getFeaturesFilterFunction shall filter getGeometry", function () {
            const webglLayer = new WebGLLayer(layerAttrs),
                featuresFilterFunction = webglLayer.getFeaturesFilterFunction(layerAttrs),
                features = [{
                    id: "1",
                    getGeometry: () => sinon.stub()
                },
                {
                    id: "2",
                    getGeometry: () => undefined
                }];

            expect(typeof featuresFilterFunction).to.be.equals("function");
            expect(featuresFilterFunction(features).length).to.be.equals(1);

        });
        it("getFeaturesFilterFunction shall filter bboxGeometry", function () {
            layerAttrs.bboxGeometry = {
                intersectsCoordinate: (coord) => {
                    if (coord[0] === 0.5 && coord[1] === 0.5) {
                        return true;
                    }
                    return false;
                },
                getExtent: () => [0, 0, 1, 1]
            };
            const webglLayer = new WebGLLayer(layerAttrs),
                featuresFilterFunction = webglLayer.getFeaturesFilterFunction(layerAttrs),
                features = [{
                    id: "1",
                    getGeometry: () => {
                        return {
                            getExtent: () => [0, 0, 1, 1]
                        };

                    }
                },
                {
                    id: "2",
                    getGeometry: () => undefined
                },
                {
                    id: "3",
                    getGeometry: () => {
                        return {
                            getExtent: () => [1, 1, 2, 2]
                        };
                    }
                }];

            expect(typeof featuresFilterFunction).to.be.equals("function");
            expect(featuresFilterFunction(features).length).to.be.equals(1);
            expect(featuresFilterFunction(features)[0].id).to.be.equals("1");
        });
    });
    describe("afterLoading", () => {
        const features = [new Feature()];

        it("should call the format functions for features", () => {
            const
                webglLayer = new WebGLLayer(layerAttrs),
                formatGeomSpy = sinon.stub(webglLayer, "formatFeatureGeometry"),
                formatStylesSpy = sinon.stub(webglLayer, "formatFeatureStyles"),
                formatDataSpy = sinon.stub(webglLayer, "formatFeatureData");

            webglLayer.afterLoading(features, layerAttrs);
            expect(formatGeomSpy.calledOnceWith(features[0])).to.be.true;
            expect(formatStylesSpy.calledOnceWith(features[0], undefined)).to.be.true;
            expect(formatDataSpy.calledOnceWith(features[0], undefined)).to.be.true;
        });
        it("should add feature IDs", () => {
            const webglLayer = new WebGLLayer(layerAttrs);

            webglLayer.afterLoading(features, layerAttrs);
            expect(features[0].getId()).to.equal("webgl-" + layerAttrs.id + "-feature-id-" + 0);
        });
        it("should set features prop and call featuresLoaded", () => {
            const
                webglLayer = new WebGLLayer(layerAttrs),
                newFeatures = [new Feature({id: "bar"})],
                featuresLoadedSpy = sinon.stub(webglLayer, "featuresLoaded");

            webglLayer.afterLoading(newFeatures, layerAttrs);
            expect(webglLayer.features).to.equal(newFeatures);
            expect(featuresLoadedSpy.calledOnceWith(layerAttrs.id, newFeatures)).to.be.true;
        });
    });
    describe("private format and style functions", () => {
        const
            styleRule = {style: {
                polygonFillColor: [255, 0, 0, 0.5],
                polygonStrokeColor: [0, 255, 0, 0.5],
                polygonStrokeWidth: 2,
                circleFillColor: [0, 0, 255, 0.5],
                circleRadius: 6
            }},
            styleModel = {
                getRulesForFeature: () => [styleRule]
            },
            feature = new Feature({
                geometry: new Polygon([
                    [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 0]]
                ], "XYZ"),
                apple: "42",
                pear: "true",
                pumpkin: "false"
            });
        let _feature;

        describe("formatFeatureGeometry", () => {
            it("should remove any Z components from the geometry", () => {
                _feature = feature.clone();
                WebGLLayer.prototype.formatFeatureGeometry(_feature);
                expect(_feature.getGeometry().getCoordinates()[0].every(coord => coord.length === 2)).to.be.true;
            });
        });
        describe("formatFeatureData", () => {
            it("should not format excluded formats 'number' and 'boolean", () => {
                _feature = feature.clone();
                WebGLLayer.prototype.formatFeatureData(_feature, ["number", "boolean"]);
                expect(typeof _feature.get("apple")).to.equal("string");
                expect(typeof _feature.get("pear")).to.equal("string");
                expect(typeof _feature.get("pumpkin")).to.equal("string");
            });
            it("should format numbers and booleans", () => {
                _feature = feature.clone();
                WebGLLayer.prototype.formatFeatureData(_feature, []);
                expect(typeof _feature.get("apple")).to.equal("number");
                expect(typeof _feature.get("pear")).to.equal("boolean");
                expect(typeof _feature.get("pumpkin")).to.equal("boolean");
            });
        });
        describe("formatFeatureStyles", () => {
            it("bind the styling rule from the styleModel to each feature", () => {
                _feature = feature.clone();
                WebGLLayer.prototype.formatFeatureStyles(_feature, styleModel);
                expect(_feature._styleRule).to.equal(styleRule);
            });
        });
        describe("getStyleFunctions", () => {
            it("should read the style from styleRule and pack them to single float", () => {
                const renderFunctions = WebGLLayer.prototype.getRenderFunctions();

                _feature = feature.clone();
                WebGLLayer.prototype.formatFeatureStyles(_feature, styleModel);
                expect(renderFunctions.fill.attributes.color(_feature)).to.equal(packColor(styleRule.style.polygonFillColor));
                expect(renderFunctions.fill.attributes.opacity(_feature)).to.equal(styleRule.style.polygonFillColor[3]);
                expect(renderFunctions.stroke.attributes.color(_feature)).to.equal(packColor(styleRule.style.polygonStrokeColor));
                expect(renderFunctions.stroke.attributes.width(_feature)).to.equal(styleRule.style.polygonStrokeWidth);
                expect(renderFunctions.stroke.attributes.opacity(_feature)).to.equal(styleRule.style.polygonStrokeColor[3]);
                expect(renderFunctions.point.attributes.color(_feature)).to.equal(packColor(styleRule.style.circleFillColor));
                expect(renderFunctions.point.attributes.size(_feature)).to.equal(styleRule.style.circleRadius);
                expect(renderFunctions.point.attributes.opacity(_feature)).to.equal(styleRule.style.circleFillColor[3]);
            });
            it("should return default values if no style rule is found", () => {
                const renderFunctions = WebGLLayer.prototype.getRenderFunctions();

                _feature = feature.clone();
                expect(feature._styleRule).to.be.undefined;
                expect(typeof renderFunctions.fill.attributes.color(_feature)).to.equal("number");
                expect(typeof renderFunctions.fill.attributes.opacity(_feature)).to.equal("number");
                expect(typeof renderFunctions.stroke.attributes.color(_feature)).to.equal("number");
                expect(typeof renderFunctions.stroke.attributes.width(_feature)).to.equal("number");
                expect(typeof renderFunctions.stroke.attributes.opacity(_feature)).to.equal("number");
                expect(typeof renderFunctions.point.attributes.color(_feature)).to.equal("number");
                expect(typeof renderFunctions.point.attributes.size(_feature)).to.equal("number");
                expect(typeof renderFunctions.point.attributes.opacity(_feature)).to.equal("number");
            });
        });
    });
    describe("updateSource", () => {
        it("updateSource shall refresh source if 'sourceUpdated' is false", function () {
            const webglLayer = new WebGLLayer(layerAttrs),
                layer = webglLayer.get("layer"),
                spy = sinon.spy(layer.getSource(), "refresh");

            expect(webglLayer.get("sourceUpdated")).to.be.false;
            webglLayer.updateSource();
            expect(spy.calledOnce).to.be.true;
            expect(webglLayer.get("sourceUpdated")).to.be.true;
        });
        it("updateSource shall not refresh source if 'sourceUpdated' is true", function () {
            layerAttrs.sourceUpdated = true;
            const webglLayer = new WebGLLayer(layerAttrs),
                layer = webglLayer.get("layer"),
                spy = sinon.spy(layer.getSource(), "refresh");

            expect(webglLayer.get("sourceUpdated")).to.be.true;
            webglLayer.updateSource();
            expect(spy.notCalled).to.be.true;
            expect(webglLayer.get("sourceUpdated")).to.be.true;
        });
    });
    describe("clearSource", () => {
        it("should remove all features from the source, but not the layer object", () => {
            const
                feature = new Feature(),
                webglLayer = new WebGLLayer(layerAttrs);

            webglLayer.features = [feature];
            webglLayer.source.addFeatures([feature]);
            webglLayer.clearSource();

            expect(webglLayer.source.getFeatures()).to.have.lengthOf(0);
            expect(webglLayer.features).to.have.lengthOf(1);
        });
    });
    describe("createLegend", () => {
        it("createLegend shall set legend", function () {
            layerAttrs.legendURL = "https://legendUrl";
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.get("legend")).to.be.deep.equals([layerAttrs.legendURL]);
        });
        it("createLegend shall set not secured legend", function () {
            let count1 = 0,
                count2 = 0;

            sinon.stub(Radio, "request").callsFake((...args) => {
                let ret = null;

                args.forEach(arg => {
                    if (arg === "returnModelById") {
                        ret = {
                            id: "id",
                            getGeometryTypeFromWFS: () => {
                                ++count1;
                            },
                            getGeometryTypeFromSecuredWFS: () => {
                                ++count2;
                            },
                            getLegendInfos: () => ["legendInfos"]
                        };
                    }
                });
                return ret;
            });
            layerAttrs.legend = true;
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.get("legend")).not.to.be.true;
            expect(count1).to.be.equals(1);
            expect(count2).to.be.equals(0);
        });
        it("createLegend shall set secured legend", function () {
            let count1 = 0,
                count2 = 0;

            sinon.stub(Radio, "request").callsFake((...args) => {
                let ret = null;

                args.forEach(arg => {
                    if (arg === "returnModelById") {
                        ret = {
                            id: "id",
                            getGeometryTypeFromWFS: () => {
                                ++count1;
                            },
                            getGeometryTypeFromSecuredWFS: () => {
                                ++count2;
                            },
                            getLegendInfos: () => ["legendInfos"]
                        };
                    }
                });
                return ret;
            });
            layerAttrs.legend = true;
            sourceLayerAttrs.isSecured = true;
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.get("legend")).not.to.be.true;
            expect(count1).to.be.equals(0);
            expect(count2).to.be.equals(1);
        });
    });
    describe("functions for features", () => {
        const features = [
            new Feature(),
            new Feature(),
            new Feature()
        ];

        features.forEach((feature, i) => feature.setId(i.toString()));
        it("hideAllFeatures", function () {
            const webglLayer = new WebGLLayer(layerAttrs),
                layer = webglLayer.get("layer"),
                clearSpy = sinon.spy(layer.getSource(), "clear");

            webglLayer.features = features;
            webglLayer.source.addFeatures(features);

            webglLayer.hideAllFeatures();
            expect(clearSpy.calledOnce).to.be.true;
            expect(webglLayer.source.getFeatures().length).to.equal(0);
            expect(webglLayer.features.length).to.equal(3);
        });
        it("showAllFeatures", function () {
            const webglLayer = new WebGLLayer(layerAttrs),
                layer = webglLayer.get("layer"),
                hideSpy = sinon.spy(webglLayer, "hideAllFeatures"),
                addSpy = sinon.spy(layer.getSource(), "addFeatures");

            sinon.stub(layer.getSource(), "getFeatures").returns(features);
            webglLayer.showAllFeatures();

            expect(hideSpy.calledOnce).to.be.true;
            expect(addSpy.calledOnce).to.be.true;
            expect(webglLayer.source.getFeatures().length).to.equal(3);
        });
        it("showFeaturesByIds", function () {
            const webglLayer = new WebGLLayer(layerAttrs),
                layer = webglLayer.get("layer"),
                hideSpy = sinon.spy(webglLayer, "hideAllFeatures"),
                addSpy = sinon.spy(layer.getSource(), "addFeatures");

            webglLayer.features = features;
            webglLayer.showFeaturesByIds(["1"]);

            expect(hideSpy.calledOnce).to.be.true;
            expect(addSpy.calledOnce).to.be.true;
            expect(webglLayer.source.getFeatures().length).to.be.equals(1);
        });
    });

    describe("isDisposed", () => {
        it("isDisposed should return false if layer exists", () => {
            const webglLayer = new WebGLLayer(layerAttrs);

            expect(webglLayer.isDisposed()).to.be.false;
        });
        it("isDisposed should return true if layer doesnt exist", () => {
            const webglLayer = new WebGLLayer(layerAttrs);

            webglLayer.layer = undefined;
            expect(webglLayer.isDisposed()).to.be.true;
        });
        it("isDisposed should return true if layer was disposed", () => {
            const webglLayer = new WebGLLayer(layerAttrs);

            webglLayer.layer.dispose();
            expect(webglLayer.isDisposed()).to.be.true;
        });
    });
    describe("setIsSelected", () => {
        it("should be disposed if layer was removed from the map", () => {
            const webglLayer = new WebGLLayer(layerAttrs);

            sinon.stub(BaseLayer.prototype, "setIsSelected").callsFake((val) => {
                webglLayer.set("isVisibleInMap", val);
            });
            webglLayer.setIsSelected(false);
            expect(webglLayer.isDisposed()).to.be.true;
        });
        it("layer should be rebuild if doesnt exist", () => {
            const webglLayer = new WebGLLayer(layerAttrs),
                spy = sinon.spy(webglLayer, "createLayerInstance");

            sinon.stub(BaseLayer.prototype, "setIsSelected").callsFake((val) => {
                webglLayer.set("isVisibleInMap", val);
            });
            webglLayer.layer.dispose();
            webglLayer.setIsSelected(true);
            expect(spy.calledOnce).to.be.true;
            expect(webglLayer.isDisposed()).to.be.false;
        });
    });
});
