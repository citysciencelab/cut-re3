import {expect} from "chai";
import sinon from "sinon";
import FilterApi from "../../../interfaces/filter.api";
import rawLayerList from "@masterportal/masterportalapi/src/rawLayerList";

describe("src/modules/tools/filter/interfaces/filter.api.js", () => {

    describe("setServiceByLayerModel", () => {
        let layerId, layerModel, sourceLayerList, onerror;

        before(() => {
            sinon.stub(rawLayerList, "getLayerWhere").callsFake((obj) => {
                return sourceLayerList?.find(rawLayer => rawLayer.id === obj.id);
            });
        });

        beforeEach(() => {
            onerror = (error) => console.error(error);
        });

        afterEach(() => {
            sinon.restore();
        });

        it("should set service based on source layer if WebGL layer provided", () => {
            layerId = "webgl";
            layerModel = {
                get: (key) => {
                    switch (key) {
                        case "typ":
                            return "WebGL";
                        case "sourceId":
                            return "123";
                        default:
                            return undefined;
                    }
                }
            };
            sourceLayerList = [{
                id: "123",
                typ: "GeoJSON",
                url: "www.abc.xyz"
            }];

            const filterApi = new FilterApi();

            filterApi.setServiceByLayerModel(layerId, layerModel, false, onerror);
            expect(filterApi.service).to.deep.equal({
                type: "geojson",
                extern: false,
                layerId: "webgl",
                url: "www.abc.xyz"
            });
        });
        it("should use original WebGL layer no source layer provided", () => {
            layerId = "webgl";
            layerModel = {
                get: (key) => {
                    switch (key) {
                        case "typ":
                            return "WebGL";
                        case "sourceId":
                            return "GeoJSON";
                        case "url":
                            return "www.foo.bar";
                        default:
                            return undefined;
                    }
                }
            };
            sourceLayerList = [{
                id: "123",
                typ: "WFS",
                featureNS: "namespace/xyz",
                url: "www.abc.xyz",
                featureType: "feature-type"
            }];

            const filterApi = new FilterApi();

            filterApi.setServiceByLayerModel(layerId, layerModel, false, onerror);
            expect(filterApi.service).to.deep.equal({
                type: "geojson",
                extern: false,
                layerId: "webgl",
                url: "www.foo.bar"
            });
        });
    });
});
