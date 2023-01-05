import WFSLayer from "../../../src/core/layers/wfs";

const actions = {
  /**
   * Increases the count state.
   *
   * @param {Object} context actions context object.
   * @returns {void}
   */
  async fetchProcesses({ state, commit }) {
    const response = await fetch("http://localhost:3000/api/processes", {
      headers: { "content-type": "application/json" },
    }).then((res) => res.json());

    commit("setProcesses", response.processes);
  },

  /**
   * Increases the count state.
   *
   * @param {Object} context actions context object.
   * @returns {void}
   */
  async fetchProcess({ state, commit }, processIndex) {
    const process = state.processes[processIndex];
    const response = await fetch(
      `http://localhost:3000/api/processes/${process.id}`,
      {
        headers: { "content-type": "application/json" },
      }
    ).then((res) => res.json());

    commit("setProcess", response);
  },

  async addLayerToStore({ dispatch }) {
    const wfsLayer = new WFSLayer({
      styleId: "defaultMapMarkerPoint",
      id: "999999",
      name: "TestLayer",
      url: "http://localhost:3000/geoserver/wtf/ows",
      typ: "WFS",
      featureType: "wtf:results_XS",
      format: "application/json",
      version: "1.0.0",
      featureNS: "http://www.deegree.org/app",
      gfiAttributes: "showAll",
      // wfsFilter: "ressources/xmlFilter/filterSchulenStadtteilschulen",
      layerAttribution: "nicht vorhanden",
      legend: false,
      isSecured: false,
      // propertyNames: [
      //   "bezirk_name",
      //   "stadtteil_name",
      //   "anzahl_sus_primarstufe",
      //   "geom",
      // ],
      // authenticationUrl:
      //   "https://geodienste.hamburg.de/HH_WMS_DOP10?SERVICE=WFS&VERSION=1.1.0&REQUEST=DescribeFeatureType",
      // datasets: [
      //   {
      //     md_id: "2FC4BBED-350C-4380-B138-4222C28F56C6",
      //     rs_id: "HMDK/6f62c5f7-7ea3-4e31-99ba-97407b1af9ba",
      //     md_name: "Verkehrslage auf Autobahnen (Schleifen) Hamburg",
      //     bbox: "461468.97,5916367.23,587010.91,5980347.76",
      //     kategorie_opendata: ["Transport und Verkehr"],
      //     kategorie_inspire: ["nicht INSPIRE-identifiziert"],
      //     kategorie_organisation:
      //       "Behörde für Wirtschaft, Verkehr und Innovation",
      //   },
      // ],
    });

    const layer = wfsLayer.get("layer");

    console.log(layer);
    dispatch("Maps/setLayersAlwaysOnTop", [layer], { root: true });

    wfsLayer.toggleIsVisibleInMap(true);
  },
};

export default actions;
