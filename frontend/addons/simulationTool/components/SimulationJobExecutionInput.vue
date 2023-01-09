<script>
export default {
  name: "SimulationJobExecutionInput",
  props: ["inputKey", "schema", "title", "value"],
  emits: ["change"],
  methods: {
    handleArrayValueChange(index, valueAtIndex) {
      const newValue = [...this.value];
      newValue[index] = valueAtIndex;
      this.$emit("change", newValue);
    },
    handleArrayValueDeletion(index) {
      const newValue = [...this.value];
      newValue.splice(index, 1);
      this.$emit("change", newValue);
    },
  },
};
</script>

<template>
  <input
    v-if="schema.type === 'string'"
    class="form-control"
    :key="`input_${inputKey}`"
    :id="`input_${inputKey}`"
    :name="`input_${inputKey}`"
    type="text"
    :minLength="schema.minLength"
    :maxLength="schema.maxLength"
    :pattern="schema.pattern"
    :placeholder="schema.default"
    :value="value"
    @input="$emit('change', $event.target.value)"
  />

  <input
    v-else-if="schema.type === 'numeric'"
    class="form-control"
    :key="`input_${inputKey}`"
    :id="`input_${inputKey}`"
    :name="`input_${inputKey}`"
    type="number"
    :min="schema.minimum"
    :max="schema.maximum"
    :placeholder="schema.default"
    :value="value"
    @input="$emit('change', Number($event.target.value))"
  />

  <input
    v-else-if="schema.type === 'boolean'"
    class="form-check-input"
    :key="`input_${inputKey}`"
    :id="`input_${inputKey}`"
    :name="`input_${inputKey}`"
    type="checkbox"
    :placeholder="schema.default"
    :value="value"
    @input="$emit('change', $event.target.checked)"
  />

  <div
    v-else-if="schema.type === 'array'"
    :key="`input_${inputKey}_${value?.length}`"
    class="d-flex flex-column gap-1"
  >
    <div
      v-for="(_, index) in value"
      :key="`input_${inputKey}_${index}`"
      class="d-flex align-items-center gap-2"
    >
      <SimulationJobExecutionInput
        :inputKey="index"
        :schema="schema.items"
        :value="value[index]"
        @change="handleArrayValueChange(index, $event)"
      />
      <span
        v-if="value.length > 1"
        class="bootstrap-icon"
        @click="handleArrayValueDeletion(index)"
      >
        <i class="bi-x-lg"></i>
      </span>
    </div>

    <button
      v-if="!schema.maxItems || value?.length < schema.maxItems"
      :key="`input_${inputKey}_array_add_button`"
      type="button"
      class="btn btn-sm btn-secondary"
      @click="$emit('change', [...value, ''])"
    >
      <i class="bi-plus-circle"></i> Add {{ title }} value
    </button>
  </div>
</template>
