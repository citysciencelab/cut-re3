<script>
export default {
  name: "SimulationProcess",
  props: ["processId"],
  emits: ["close", "selected"],
  data() {
    return { process: null, jobs: null, inputs: {}, loadingJobs: false };
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
    async execute(event) {
      event.preventDefault();
      const processId = this.process.id;
      const body = { mode: "async", inputs: this.inputs };
      await fetch(
        `http://localhost:3000/api/processes/${processId}/execution`,
        {
          method: "POST",
          body: JSON.stringify(body),
          headers: { "Content-Type": "application/json" },
        }
      ).then((res) => res.json());
      this.fetchJobs(processId);
    },
  },
  mounted() {
    this.fetchProcess(this.processId);
    this.fetchJobs(this.processId);
  },
};
</script>

<template>
  <div v-if="process">
    <h1>{{ process.title }}</h1>

    <a href="#" @click="$emit('close')">Back</a>

    <p>{{ process.description }}</p>

    <h2>Jobs</h2>
    <ul v-if="jobs">
      <div v-if="jobs.length === 0">No jobs yet</div>
      <li v-for="job in jobs">
        {{ new Date(job.job_start_datetime).toLocaleString() }}:
        <b>{{ job.status }}</b
        >{{ " " }}
        <span style="color: salmon" v-if="job.status === 'failed'">{{
          job.message
        }}</span>

        <a
          v-if="job.status === 'successful'"
          href="#"
          @click="$emit('selected', job.jobID)"
          >view results</a
        >
      </li>
      <div v-if="loadingJobs">Updating Jobs...</div>
    </ul>

    <h2>Execute</h2>
    <form>
      <div v-for="(input, key) in process.inputs" class="inputs">
        <label :title="input.description" :for="`input_${key}`"
          >{{ input.title }}:</label
        >

        <!-- 

          [
            {
              "title": "String",
              "description": "A string parameter",
              "schema": {
                "type": "string", // array | boolean | integer | number | object | string
                "maxLength": 1,
                "minLength": 2,
                "pattern": "",
                "default": "hello"
              },
              "minOccurs": 0,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            },
            {
              "title": "Boolean",
              "description": "A boolean parameter",
              "schema": {
                "type": "boolean",
                "default": 456
              },
              "minOccurs": 1,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            },
            {
              "title": "Number",
              "description": "A number parameter",
              "schema": {
                "type": "number",
                "minimum": 2,
                "maximum": 3,
                "default": 456
              },
              "minOccurs": 1,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            },
            {
              "title": "Array of numbers",
              "description": "An array parameter",
              "schema": {
                "type": "array",
                "minItems": 0,
                "maxItems": 3,
                "items": {
                  "type": "number"
                }
              },
              "minOccurs": 1,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            }
          ]


         -->
        <input
          v-if="input.schema.type === 'string'"
          :id="`input_${key}`"
          :name="`input_${key}`"
          type="text"
          v-model="inputs[key]"
        />

        <input
          v-if="input.schema.type !== 'string'"
          :id="`input_${key}`"
          :name="`input_${key}`"
          type="number"
          min="3"
          v-model.number="inputs[key]"
        />
      </div>
      <br />
      <button type="submit" @click="execute">Run job</button>
    </form>
  </div>

  <div v-else>Loading...</div>
</template>

<style lang="scss" scoped>
.inputs label {
  min-width: 9em;
  text-align: right;
  margin-bottom: 1em;
}
</style>
