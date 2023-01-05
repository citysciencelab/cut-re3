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
    <h3>Models</h3>

    <table class="table">
      <thead>
        <tr>
          <th scope="col" class="col-4">Model Name</th>
          <th scope="col" class="col-6">Description</th>
          <th scope="col"></th>
        </tr>
      </thead>
      <tbody>
        <template v-if="processes?.length">
          <tr v-for="process in processes" :key="process.id">
            <th scope="row">{{ process.title }}</th>
            <td>{{ process.description }}</td>
            <td>
              <a href="#" @click="$emit('selected', process.id)">Details</a>
            </td>
          </tr>
        </template>

        <tr v-else class="placeholder-glow" aria-hidden>
          <td><span class="placeholder d-block" /></td>
          <td><span class="placeholder d-block" /></td>
          <td><span class="placeholder d-block" /></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss" scoped>
h3 {
  position: sticky;
  top: -1.25rem;
  margin: -1.25rem -1.25rem 0;
  padding: 1.25rem 1.25rem 0.5rem;
  background: white;
}
</style>
