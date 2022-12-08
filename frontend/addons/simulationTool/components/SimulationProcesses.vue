<script>
export default {
  name: "SimulationProcesses",
  props: ["processes"],
  emits: ["selected"],
  data() {
    return {};
  },
  mounted() {},
};
</script>

<template>
  <div>
    <h1>Models</h1>

    <ul v-if="processes">
      <li v-for="(process, index) in processes" :key="processes.id">
        <h2>{{ process.title }}</h2>
        <p>{{ process.description }}</p>
        <a href="#" @click="$emit('selected', process.id)">Details</a>
      </li>
    </ul>

    <div v-else>Loading...</div>

    <!-- <pre>{{ JSON.stringify(processes, null, 2) }}</pre> -->
  </div>
</template>

<style lang="scss" scoped></style>
