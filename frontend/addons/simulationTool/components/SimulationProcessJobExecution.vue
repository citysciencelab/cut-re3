<script>
import Vue from "vue";
import SimulationJobExecutionInput from "./SimulationJobExecutionInput.vue";

export default {
  name: "SimulationProcessJobExecution",
  props: ["processId", "inputsConfig"],
  emits: ["executed"],
  components: { SimulationJobExecutionInput },
  data() {
    return {
      executionValues: {},
    };
  },
  watch: {
    /**
     * Listens to inputs config changes.
     * @returns {void}
     */
    inputsConfig(newInputsConfig) {
      this.resetExecutionValues(newInputsConfig);
    },
  },
  methods: {
    updateExecutionValue(key, value) {
      Vue.set(this.executionValues, key, value);
    },
    resetExecutionValues(newInputsConfig = this.inputsConfig) {
      this.executionValues = {};
      Object.entries(newInputsConfig).forEach(([key, input]) => {
        if (input.schema.type === "array") {
          Vue.set(this.executionValues, key, [""]);
        }
      });
    },
    async execute(event) {
      event.preventDefault();

      const formIsValid = this.$refs.form.reportValidity();

      if (formIsValid) {
        const processId = this.processId;
        const body = { mode: "async", inputs: this.executionValues };

        await fetch(
          `http://localhost:3000/api/processes/${processId}/execution`,
          {
            method: "POST",
            body: JSON.stringify(body),
            headers: { "Content-Type": "application/json" },
          }
        ).then((res) => res.json());

        this.resetExecutionValues();
        this.$emit("executed");
      }
    },
  },
  mounted() {
    this.resetExecutionValues(this.inputsConfig);
  },
};
</script>

<template v-if="Object.values(inputsConfig).length">
  <section>
    <h4>Execute Job</h4>

    <form class="execution-form" ref="form">
      <template v-for="(input, key) in inputsConfig">
        <label
          :title="input.description"
          :for="`input_${key}`"
          :key="`label_${key}`"
        >
          {{ input.title }}:
        </label>

        <SimulationJobExecutionInput
          :key="`input_${key}`"
          :inputKey="key"
          :schema="input.schema"
          :title="input.title"
          :value="executionValues[key]"
          @change="updateExecutionValue(key, $event)"
        />
      </template>

      <button
        class="btn btn-primary btn-sm"
        type="submit"
        @click="execute"
        :disabled="
          !Object.entries(executionValues).filter(([, value]) => value != null)
            .length
        "
      >
        Run job
      </button>
    </form>
  </section>
</template>

<style lang="scss" scoped>
.execution-form {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem;
}

.execution-form label {
  margin-top: 0.375rem;
  text-align: right;
}

.execution-form input[type="checkbox"] {
  margin: 0.5625rem 0 0.5rem;
}

.execution-form button {
  grid-column: 2;
}
</style>
