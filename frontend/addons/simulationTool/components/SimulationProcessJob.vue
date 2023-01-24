<script>
import Chart from "chart.js";
import { WFS } from "ol/format";
import { and, equalTo } from "ol/format/filter";
import { getFeaturePOST } from "../../../src/api/wfs/getFeature";

export default {
    name: "SimulationProcessJob",
    props: ["jobId", "processId"],
    emits: ["close"],
    data() {
        return {
            job: null, // the loaded job data
            chart: null, // the chart.js chart
            chartType: "line", // the currently rendered chart type
            layer: null, // the map layer used for this job
            displayMapFilters: [], // internally used filters settings
            mapFilters: [], // the filter settings
            filterOnClient: false, // flag wether server or clint filtering will be used, read from the job's layer config
        };
    },
    watch: {
        chartType() {
            this.renderChart();
        },
        mapFilters: {
            // watch (deeply) for changes in mapFilters to initiate new WFS requests or filter data in client
            handler: function (newVal, oldVal) {
                if (!oldVal.length) {
                    return;
                }

                this.updateLayer(newVal);
            },
            deep: true,
        },
    },
    methods: {
        /**
         * Fetches the job details
         * @param {String} jobId Id of the job to fetch
         */
        async fetchJob(jobId) {
            this.job = await fetch(`${Config.simulationApiUrl}/jobs/${jobId}`, {
                headers: { "content-type": "application/json" },
            }).then((res) => res.json());
        },

        /**
         * Calculates and returns the data to render charts.
         * TODO: this is currently bound to a specific model, need to discuss how this will be defined per model
         */
        getChartData() {
            const result = {};
            const graphData = this.layer
                .get("layerSource")
                .getFeatures()
                .map((feature) => {
                    const properties = { ...feature.getProperties() };
                    delete properties.geometry;
                    return properties;
                });

            for (const data of graphData) {
                // Count agents per Stadtviertel
                const id = data.AgentID.split("-")[0];
                result[id] = result[id] ? result[id] + 1 : 1;
            }

            return {
                labels: Object.keys(result),
                data: Object.values(result),
            };
        },

        /**
         * Render new chart or update existing one
         */
        renderChart() {
            const chartData = this.getChartData();
            const data = {
                labels: chartData.labels,
                datasets: [
                    {
                        data: chartData.data,
                        backgroundColor: "cornflowerblue",
                    },
                ],
            };

            // Update or remove previous chart
            if (this.chart && this.chart.config.type === this.chartType) {
                this.chart.data.datasets[0].data = data.datasets[0].data;
                this.chart.update();
                return;
            } else {
                this.chart?.destroy();
            }

            // Render new chart
            const context = this.$refs.chart.getContext("2d");
            this.chart = new Chart(context, {
                type: this.chartType,
                data,
                options: {
                    legend: {
                        display: false,
                    },
                },
            });
        },

        /**
         * Get the corresponding layer configured in the services file
         */
        createLayer() {
            if (!this.layer) {
                this.layer = Radio.request(
                    "ModelList",
                    "getModelByAttributes",
                    {
                        isSimulationLayer: true,
                        simModelId: this.processId,
                    }
                );

                if (!this.layer) {
                    throw new Error(
                        `No matching layer found for simModelId '${this.processId}`
                    );
                }

                // read and save the load mode for this layer/model
                this.filterOnClient = Boolean(
                    this.layer.attributes.filterOnClient
                );
            }
        },

        /**
         * Updates the layer features
         */
        async updateLayer() {
            if (this.filterOnClient) {
                this.updateLayerClient();
            } else {
                this.updateLayerServer();
            }
        },

        /**
         * Update the layer features, filtered on the server via WFS filter
         */
        async updateLayerServer() {
            const filters = this.mapFilters.filter((mf) => mf.active);

            let olFilter = undefined;

            if (filters.length) {
                olFilter =
                    filters.length < 2
                        ? equalTo(filters[0].key, filters[0].value)
                        : and(
                              ...filters.map((mf) => equalTo(mf.key, mf.value))
                          );
            }

            const mapProjection = Radio.request("MapView", "getProjection");
            const response = await getFeaturePOST(this.layer.get("url"), {
                featureTypes: [`CUT:${this.jobId}`],
                srsName: mapProjection.getCode(),
                filter: olFilter,
            });

            const dataProjetion = new WFS().readProjection(response);
            const features = new WFS().readFeatures(
                response,
                mapProjection,
                dataProjetion
            );

            this.updateSource(features);
            this.renderChart();
        },

        /**
         * Update the layer features, loads all data initially and filters on the client
         */
        async updateLayerClient() {
            if (!this.features) {
                const mapProjection = Radio.request("MapView", "getProjection");
                const response = await getFeaturePOST(this.layer.get("url"), {
                    featureTypes: [`CUT:${this.jobId}`],
                    format: "application/json",
                    srsName: mapProjection.getCode(),
                });
                const dataProjetion = new WFS().readProjection(response);

                // generate ol features and reproject data
                this.features = new WFS().readFeatures(
                    response,
                    mapProjection,
                    dataProjetion
                );
            }

            // filter features by mapFilters
            const filteredFeatures = this.features.filter((feature) => {
                return this.mapFilters.every((mf) => {
                    if (!mf.active) {
                        // if filter is not active this check is passed
                        return true;
                    }

                    const { key, value } = mf;
                    const properties = feature.getProperties();
                    const featureValue =
                        typeof value === "number"
                            ? Number(properties[key])
                            : properties[key];

                    return value === featureValue;
                });
            });

            this.updateSource(filteredFeatures);
            this.renderChart();
        },

        /**
         * Updates the layer's source
         * @param {ol.Feature[]} features The feature to show on the map
         */
        updateSource(features) {
            const source = this.layer.get("layerSource");
            source.clear();
            source.addFeatures(features);
        },

        /**
         * Initially set the job's filter values retrieved from the job's config
         */
        initMapFilters() {
            this.mapFilters = [
                { key: "Step", value: 0, active: true, min: 0, max: 100 },
                { key: "iteration", value: 0, active: false },
                {
                    key: "AgentID",
                    value: "",
                    active: false,
                    options: ["Bahrenfeld-1", "Rotherbaum-0"],
                },
            ];
            this.displayMapFilters = structuredClone(this.mapFilters);
        },

        /**
         * Hlper function to update a filter value
         * @param {String} key The filter key
         * @param {String | Number} value The filter's new value
         * @param {Boolean} active If the filter is active
         */
        setMapFilter(key, value, active) {
            const filter = this.displayMapFilters.find((mf) => mf.key === key);
            filter.value = value;
            filter.active = active;
        },

        /**
         * Commtis the current display filters to the actual applied filter values.
         * Note that new requests are only fired when the applied filters object changes.
         */
        commitMapFilters() {
            this.mapFilters = structuredClone(this.displayMapFilters);
        },
    },
    async mounted() {
        await this.fetchJob(this.jobId);
        this.initMapFilters();
        this.createLayer();
        this.updateLayer();
    },

    beforeDestroy() {
        // clear the layer's source to remove everything from the map
        this.layer?.layer.getSource().clear();
    },
};
</script>

<template>
    <div>
        <div class="job-details">
            <div :class="{ 'job-header': true, 'placeholder-glow': !job }">
                <a
                    class="bootstrap-icon"
                    href="#"
                    @click="$emit('close')"
                    title="Back"
                >
                    <i class="bi-chevron-left"></i>
                </a>

                <h3 :class="{ placeholder: !job }" :aria-hidden="!job">
                    {{
                        job
                            ? `Job "${
                                  job.parameters.inputs.name ||
                                  new Date(job.started).toLocaleString()
                              }"`
                            : "Loading job name"
                    }}
                </h3>
            </div>

            <div v-if="job" class="job-data">
                <div>
                    Status:
                    <span
                        :class="{
                            status: true,
                            'text-bg-info':
                                job.status !== 'successful' &&
                                job.status !== 'failed',
                            'text-bg-success': job.status === 'successful',
                            'text-bg-danger': job.status === 'failed',
                        }"
                    >
                        {{ job.status }}
                    </span>
                </div>
                <div>
                    Started:
                    {{ new Date(job.started).toLocaleString() }}
                </div>
                <div>Ended: {{ new Date(job.finished).toLocaleString() }}</div>
            </div>
            <p v-else class="placeholder-glow" aria-hidden>
                <span class="placeholder col-3" />
                <span class="placeholder col-4" />
                <span class="placeholder col-4" />
                <span class="placeholder col-6" />
                <span class="placeholder col-3" />
            </p>
        </div>

        <div class="job-filter" v-if="job">
            <h4>Property Filter</h4>
            <ul>
                <li v-for="filter in displayMapFilters" :key="filter.key">
                    <label>{{ filter.key }}</label>
                    <input
                        type="checkbox"
                        :checked="filter.active"
                        @change="
                            (event) => {
                                setMapFilter(
                                    filter.key,
                                    filter.value,
                                    event.target.checked
                                );
                                commitMapFilters();
                            }
                        "
                    />
                    <input
                        v-if="typeof filter.value === 'number'"
                        type="range"
                        :min="filter.min ?? 0"
                        :max="filter.max ?? 0"
                        step="1"
                        :value="filter.value"
                        :disabled="!filter.active"
                        @input="
                            (event) => {
                                setMapFilter(
                                    filter.key,
                                    Number(event.target.value),
                                    filter.active
                                );
                                if (filterOnClient) {
                                    commitMapFilters();
                                }
                            }
                        "
                        @change="
                            (event) => {
                                if (!filterOnClient) {
                                    commitMapFilters();
                                }
                            }
                        "
                    />

                    <select
                        v-else
                        class="form-select"
                        :value="filter.value"
                        :disabled="!filter.active"
                        @change="
                            (event) => {
                                setMapFilter(
                                    filter.key,
                                    event.target.value,
                                    filter.active
                                );
                                commitMapFilters();
                            }
                        "
                    >
                        <option
                            v-for="option in filter.options"
                            :value="option"
                        >
                            {{ option }}
                        </option>
                    </select>

                    <span v-if="typeof filter.value === 'number'">{{
                        filter.value
                    }}</span>
                </li>
            </ul>
        </div>

        <div class="job-graphs" v-if="job">
            <h4>Charts</h4>
            <ul class="nav nav-pills nav-fill">
                <li
                    class="nav-item"
                    v-for="type in ['line', 'radar', 'bar']"
                    :key="type"
                >
                    <a
                        :class="{
                            'nav-link': true,
                            active: chartType === type,
                        }"
                        :aria-current="chartType === type ? 'page' : false"
                        href="#"
                        @click.prevent="chartType = type"
                    >
                        {{ type.charAt(0).toUpperCase() + type.slice(1) }} Chart
                    </a>
                </li>
            </ul>

            <canvas ref="chart" width="400" height="300"></canvas>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.job-details {
    position: sticky;
    top: -1.25rem;
    margin: -1.25rem -1.25rem 1rem;
    padding: 1.25rem 1.25rem 0;
    background: white;
}

.job-details::after {
    content: "";
    display: block;
    border-bottom: 1px solid rgba(0, 0, 0, 0.25);
}

.job-header {
    display: flex;
    align-items: center;
    column-gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.job-header > * {
    margin: 0;
}

.job-data {
    display: grid;
    gap: 0.25rem;
    margin-bottom: 0.5rem;
}

.status {
    padding: 0.1em 0.5em;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.job-graphs {
    display: grid;
    gap: 1rem;
}

.job-graphs canvas {
    margin-top: 2rem;
}

.job-filter {
    padding: 1em 0;
}

.job-filter input {
    outline: none;
}

.job-filter ul {
    padding: 0;
}

.job-filter li {
    display: grid;
    padding: 1em 0;
    grid-template-columns: 5em auto 1fr minmax(2em, auto);
    gap: 1em;
    align-items: center;
}

.job-filter li label {
    font-weight: bold;
}
</style>

