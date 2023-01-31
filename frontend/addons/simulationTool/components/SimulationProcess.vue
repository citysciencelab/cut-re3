<script>
import SimulationProcessJobsTable from "./SimulationProcessJobsTable.vue";
import SimulationProcessJobExecution from "./SimulationProcessJobExecution.vue";
import Config from "../../../portal/simulation/config";

export default {
    name: "SimulationProcess",
    props: ["processId"],
    emits: ["selected", "close"],
    components: { SimulationProcessJobsTable, SimulationProcessJobExecution },
    data() {
        return {
            process: null,
            jobs: null,
            loadingJobs: false,
            apiUrl: Config.simulationApiUrl,
        };
    },
    computed: {
        inputsConfig() {
            return this.process?.inputs || {};
        },
    },
    methods: {
        /**
         * Fetches a process from the simulation backend
         * @param {String} processId
         */
        async fetchProcess(processId) {
            this.process = await fetch(
                `${this.apiUrl}/processes/${processId}`,
                {
                    headers: { "content-type": "application/json" },
                }
            ).then((res) => res.json());
        },
        /**
         * Fetches the job list from the simulation backend
         * @param {String} processId
         */
        async fetchJobs(processId) {
            this.loadingJobs = true;
            this.jobs = await fetch(
                `${this.apiUrl}/jobs?processID=${processId}`
            )
                .then((res) => res.json())
                .then((json) => json.jobs);

            this.loadingJobs = false;

            // update jobs list if there are jobs running
            if (
                this.jobs.some((job) =>
                    ["accepted", "running"].includes(job.status)
                )
            ) {
                setTimeout(() => this.fetchJobs(processId), 5000);
            }
        },
    },
    mounted() {
        this.fetchProcess(this.processId);
        this.fetchJobs(this.processId);
    },
};
</script>

<template>
    <div>
        <div class="process-details">
            <div
                :class="{
                    'process-header': true,
                    'placeholder-glow': !process,
                }"
            >
                <a
                    class="bootstrap-icon"
                    href="#"
                    @click="$emit('close')"
                    title="Back"
                >
                    <i class="bi-chevron-left"></i>
                </a>

                <h3 :class="{ placeholder: !process }" :aria-hidden="!process">
                    {{ process?.title || "Loading process name" }}
                </h3>
            </div>

            <p v-if="process">{{ process.description }}</p>
            <p v-else class="placeholder-glow" aria-hidden>
                <span class="placeholder col-3" />
                <span class="placeholder col-4" />
                <span class="placeholder col-4" />
                <span class="placeholder col-6" />
                <span class="placeholder col-3" />
            </p>
        </div>

        <div class="process-content" v-if="process">
            <SimulationProcessJobsTable
                :process="process"
                :jobs="jobs"
                :loadingJobs="loadingJobs"
                v-on="$listeners"
            />

            <SimulationProcessJobExecution
                :processId="processId"
                :inputsConfig="inputsConfig"
                @executed="fetchJobs(processId)"
            />
        </div>
    </div>
</template>

<style lang="scss" scoped>
.process-details {
    position: sticky;
    top: -1.25rem;
    margin: -1.25rem -1.25rem 2rem;
    padding: 1.25rem 1.25rem 0;
    background: white;
}

.process-details::after {
    content: "";
    display: block;
    // border-bottom: 1px solid rgba(0, 0, 0, 0.25);
}

.process-header {
    display: flex;
    align-items: center;
    column-gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.process-header > * {
    margin: 0;
}

.process-content {
    display: grid;
    gap: 2rem;
}
</style>

