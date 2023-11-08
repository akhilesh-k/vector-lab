import { defineStore } from "pinia";
import { ref } from "vue";
export const useRouterMetaDataStore = defineStore(
  "router-metadata-store",
  () => {
    const metaData = ref({});
    return { metaData };
  }
);
