<script>
export default {
  name: "SimulationProcess",
  props: ["processId"],
  emits: ["close"],
  data() {
    return { process: null, jobs: null, inputs: {} };
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
      this.jobs = await fetch(`http://localhost:3000/api/jobs`)
        .then((res) => res.json())
        .then((json) => json.jobs.filter((job) => job.processID === processId));
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
      <li v-for="job in jobs">
        {{ new Date(job.job_start_datetime).toLocaleString() }}:
        <b>{{ job.status }}</b
        >{{ " " }}
        <a v-if="job.status === 'successful'" href="#">view results</a>
      </li>
    </ul>

    <h2>Execute</h2>
    <form>
      <div v-for="(input, key) in process.inputs" class="inputs">
        <label :title="input.description" :for="`input_${key}`"
          >{{ input.title }}:</label
        >
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
          v-model.number="inputs[key]"
        />
      </div>
      {{ JSON.stringify(inputs, null, 2) }}
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
