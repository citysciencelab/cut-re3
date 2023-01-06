<script>
import SimulationProcessJobsTable from "./SimulationProcessJobsTable.vue";
import SimulationProcessJobExecution from "./SimulationProcessJobExecution.vue";

export default {
  name: "SimulationProcess",
  props: ["processId"],
  emits: ["close"],
  components: { SimulationProcessJobsTable, SimulationProcessJobExecution },
  data() {
    return {
      process: null,
      jobs: null,
      loadingJobs: false,
    };
  },
  computed: {
    inputsConfig() {
      // TODO: remove dummy data
      /**
      return {
        string: {
          title: "String",
          description: "A string parameter",
          schema: {
            type: "string", // array | boolean | integer | number | object | string
            minLength: 1,
            maxLength: 10,
            pattern: "[A-Za-z]",
            default: "hello",
          },
          minOccurs: 0,
          maxOccurs: 1,
          metadata: {
            display: "range",
          },
        },
        boolean: {
          title: "Boolean",
          description: "A boolean parameter",
          schema: {
            type: "boolean",
            default: 456,
          },
          minOccurs: 1,
          maxOccurs: 1,
          metadata: {
            display: "range",
          },
        },
        number: {
          title: "Number",
          description: "A number parameter",
          schema: {
            type: "numeric",
            minimum: 2,
            maximum: 3,
            default: 456,
          },
          minOccurs: 1,
          maxOccurs: 1,
          metadata: {
            display: "range",
          },
        },
        array: {
          title: "Array of numbers",
          description: "An array parameter",
          schema: {
            type: "array",
            minItems: 0,
            maxItems: 3,
            items: {
              type: "numeric",
            },
          },
          minOccurs: 1,
          maxOccurs: 1,
          metadata: {
            display: "range",
          },
        },
      };
      */
      return this.process?.inputs || {};
    },
  },
  methods: {
    async fetchProcess(processId) {
      this.process = await fetch(
        `http://localhost:3000/api/processes/${processId}`,
        {
          headers: { "content-type": "application/json" },
        }
      ).then((res) => res.json());
    },
    async fetchJobs(processId) {
      this.loadingJobs = true;
      this.jobs = await fetch(`http://localhost:3000/api/jobs`)
        .then((res) => res.json())
        .then((json) => json.jobs.filter((job) => job.processID === processId));

      this.loadingJobs = false;

      // update jobs list if there are jobs running
      if (
        this.jobs.some((job) => ["accepted", "running"].includes(job.status))
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
      <div :class="{ 'process-header': true, 'placeholder-glow': !process }">
        <a class="bootstrap-icon" href="#" @click="$emit('close')" title="Back">
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
        :processId="processId"
        :jobs="jobs"
        :loadingJobs="loadingJobs"
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
  margin: -1.25rem -1.25rem 1rem;
  padding: 1.25rem 1.25rem 0;
  background: white;
}

.process-details::after {
  content: "";
  display: block;
  border-bottom: 1px solid rgba(0, 0, 0, 0.25);
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
