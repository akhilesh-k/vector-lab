<script setup>
import { ref, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useRouterMetaDataStore } from "@/store";
import ExcelJS from "exceljs";
const route = useRoute();
const router = useRouter();
const metaDataStore = useRouterMetaDataStore();
const isOnAuditRoute = computed(() => metaDataStore.metaData.value.audit);
const isOnVectorRoute = computed(
  () => metaDataStore.metaData.value.vectorSearch && !auditMode.value
);
const searchTerm = ref("");
const vectorBoost = ref(3);
const page = ref(1);
const topK = ref(800);
const items = ref(40);
const union = ref(500);
const debugMode = ref(false);
const auditorEmail = ref(localStorage.getItem("auditorEmail") || "");
const lexicalCallDone = ref(false);
const hybridCallDone = ref(false);

const auditMode = ref(
  isOnAuditRoute.value &&
    !isOnVectorRoute.value &&
    auditorEmail.value?.length > 0
);
const isLexicalSearch = ref(true);
const isHybridSearch = ref(true);
const algo = ref("control");
const algoOptions = ["control", "variant1", "variant2", "variant3", "variant4"];

const lexicalProducts = ref([]);
const hybridProducts = ref([]);
const includeNdcg = ref(false);

const lexicalController = ref();
const hybridController = ref();

const markAllRelevantLexical = ref(false);
const markAllRelevantHybrid = ref(false);

const lexicalMetaData = ref({
  numFound: 0,
  responseTime: 0,
  items: 0,
});
const hybridMetaData = ref({
  numFound: 0,
  responseTime: 0,
  items: 0,
});

const lexicalHeading = computed(() => {
  const { numFound, responseTime, items } = lexicalMetaData.value;
  if (numFound != 0 && items != 0) {
    return `Displaying ${items} Lexical results out of ${numFound} products in ${
      Math.round(responseTime * 100) / 100
    } seconds`;
  } else {
    return `No lexical results found. Search took ${responseTime} seconds`;
  }
});
const hybridHeading = computed(() => {
  const { numFound, responseTime, items } = hybridMetaData.value;
  if (numFound != 0 && items != 0) {
    return `Displaying ${items} Hybrid results out of ${numFound} products in ${
      Math.round(responseTime * 100) / 100
    } seconds`;
  } else {
    return `No hybrid results found. Search took ${responseTime} seconds`;
  }
});

const buildQuery = (prefix, userQuery) => {
  var query = [];
  for (const key in userQuery) {
    query.push(
      encodeURIComponent(key) + "=" + encodeURIComponent(userQuery[key])
    );
  }
  const url = prefix + (query.length ? "?" + query.join("&") : "");
  return url;
};

const downloadXLSX = (products, auditResponse, auditType) => {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet("Audit Results");

  // Add header row
  worksheet.addRow([
    "Search Term",
    "Rank",
    "Item SKU",
    "Name",
    "Relevance",
    "Comment",
  ]);

  // Add data rows
  products.forEach((product) => {
    product.relevance = product.relevance ? 1 : 0;
    const { position, itemSku, name, relevance, comment } = product;

    let cellComment = "";
    if (Array.isArray(comment) && comment.length > 0) {
      cellComment = comment[0].trim();
    } else if (typeof comment === "string") {
      cellComment = comment.trim();
    }

    worksheet.addRow([
      searchTerm.value,
      position,
      itemSku,
      name,
      relevance,
      cellComment,
    ]);
  });

  // Add audit response
  if (includeNdcg.value) {
    worksheet.addRow(["Audit Response:", JSON.stringify(auditResponse)]);
  }

  // Create a Blob
  workbook.xlsx.writeBuffer().then((data) => {
    const blob = new Blob([data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    // Create a download link for the Blob
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${
      searchTerm.value
    }_${auditType.toLowerCase()}_audit_results.xlsx`;

    // Trigger a click event on the download link to start the download
    a.click();

    // Clean up by revoking the Blob URL
    window.URL.revokeObjectURL(url);
  });
};

const submitAudit = (auditType) => {
  let auditData = {};
  if (auditType === "LEXICAL") {
    auditData = {
      audits: lexicalProducts.value.map((product) => ({
        sku: product.sku,
        relevance: product.relevance ? 1 : 0,
        comment: product.comment,
      })),
      auditor: auditorEmail.value,
      algo: algo.value,
      searchType: "Lexical",
      pageNumber: page.value,
      searchTerm: searchTerm.value,
    };
  }
  if (auditType === "HYBRID") {
    auditData = {
      audits: hybridProducts.value.map((product) => ({
        sku: product.sku,
        relevance: product.relevance ? 1 : 0,
        comment: product.comment,
      })),
      auditor: auditorEmail.value,
      algo: algo.value,
      searchType: "Hybrid",
      pageNumber: page.value,
      searchTerm: searchTerm.value,
    };
  }
  const apiUrl = "http://xsearch-solr-vector-2.qa2-sg.cld:5000/submit-audit";

  fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(auditData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      downloadXLSX(
        auditType === "LEXICAL" ? lexicalProducts.value : hybridProducts.value,
        data,
        auditType
      );
      markAllRelevantHybrid.value = false;
      markAllRelevantLexical.value = false;
    })
    .catch((error) => {
      console.error("Error while submitting the audit:", error);
    });
};

const getProductsApi = (scope) => {
  if (lexicalController.value) {
    lexicalController.value.abort();
  }
  if (hybridController.value) {
    hybridController.value.abort();
  }

  if (scope === "LEXICAL") {
    lexicalProducts.value = [];
    lexicalCallDone.value = false;
  }
  if (scope === "HYBRID") {
    hybridProducts.value = [];
    hybridCallDone.value = false;
  }
  if (searchTerm.value?.length) {
    const urlPrefix = "http://xsearch-solr-vector-2.qa2-sg.cld:5000/search";
    const query = {
      searchTerm: searchTerm.value,
      boostValue: vectorBoost.value,
      page: page.value,
      start: (page.value - 1) * items.value,
      itemPerPage: items.value,
      vectorUnion: union.value,
      topK: topK.value,
      showFacet: false,
      channelId: "web",
      multiCateogory: true,
      intent: true,
      updateCache: false,
      QUi58PyL: debugMode.value,
      userIdentifier: 500681720,
      algo: algo.value,
    };
    if (scope === "HYBRID") {
      query.hybridQuery = isHybridSearch.value;
    }
    const urlConfig = {
      method: "GET",
      signal:
        scope === "LEXICAL"
          ? lexicalController.signal
          : hybridController.signal,
    };
    const url = buildQuery(urlPrefix, query);
    if (scope === "LEXICAL") {
      lexicalController.value = new AbortController();
    }
    if (scope === "HYBRID") {
      hybridController.value = new AbortController();
    }
    fetch(url, urlConfig)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        return res.json();
      })
      .then((data) => {
        if (scope === "LEXICAL") {
          lexicalCallDone.value = true;
          lexicalProducts.value = [];
          lexicalProducts.value = data?.products;
          lexicalMetaData.value = {
            numFound: data?.numFound,
            responseTime: data?.responseTime,
            items: data?.products.length,
          };
        }
        if (scope === "HYBRID") {
          hybridCallDone.value = true;
          hybridProducts.value = [];
          hybridProducts.value = data?.products;
          hybridMetaData.value = {
            numFound: data?.numFound,
            responseTime: data?.responseTime,
            items: data?.products.length,
          };
        }
      })
      .catch((err) => {
        console.error("ERROR: Can't convert to JSON - ", err);
      });
  }
};

const getProducts = () => {
  if (isLexicalSearch.value) {
    getProductsApi("LEXICAL");
  }
  if (isHybridSearch.value) {
    getProductsApi("HYBRID");
  }
};

const goToPDP = (url) => {
  window.open(url, "_blank");
};

const pushToAuditPage = (event) => {
  if (event.target.value === "on" && auditMode.value) {
    router.push("/audit");
  } else {
    router.push("/vector-search");
  }
};

const getPageSubHeading = () => {
  if (isOnAuditRoute.value) {
    return "Audit Results";
  } else {
    return "Vector Search";
  }
};

watch(
  () => [
    isLexicalSearch.value,
    vectorBoost.value,
    page.value,
    items.value,
    topK.value,
    union.value,
    debugMode.value,
    algo.value,
  ],
  () => {
    if (isLexicalSearch.value) {
      getProductsApi("LEXICAL");
    }
  }
);

watch(
  () => [
    isHybridSearch.value,
    vectorBoost.value,
    page.value,
    items.value,
    topK.value,
    union.value,
    debugMode.value,
    algo.value,
  ],
  () => {
    if (isHybridSearch.value) {
      getProductsApi("HYBRID");
    }
  }
);

watch(
  () => markAllRelevantLexical.value,
  () => {
    if (markAllRelevantLexical.value) {
      lexicalProducts.value.forEach((product) => {
        product.relevance = true;
      });
    } else {
      lexicalProducts.value.forEach((product) => {
        product.relevance = false;
      });
    }
  }
);

watch(
  () => markAllRelevantHybrid.value,
  () => {
    if (markAllRelevantHybrid.value) {
      hybridProducts.value.forEach((product) => {
        product.relevance = true;
      });
    } else {
      hybridProducts.value.forEach((product) => {
        product.relevance = false;
      });
    }
  }
);
watch(
  () => route.meta,
  () => {
    if (route.meta.audit) {
      auditMode.value = true;
    }
    if (route.meta.vectorSearch) {
      auditMode.value = false;
    }
  }
);
</script>

<template>
  <main class="container">
    <h3>{{ getPageSubHeading() }}</h3>
    <section class="filters">
      <div class="query-input">
        <div class="flex-col">
          <label for="searchTerm"> Enter the Search term: </label>
          <input
            v-model="searchTerm"
            id="searchTerm"
            type="text"
            placeholder="Enter the search term"
            @keypress.enter="getProducts"
          />
        </div>
      </div>

      <div class="filter-input">
        <div v-if="isOnVectorRoute" class="flex-col">
          <label for="vectorBoost"> Boost: </label>
          <input
            v-model="vectorBoost"
            id="vectorBoost"
            type="number"
            placeholder="Vector boost"
          />
        </div>
        <div v-if="isOnVectorRoute" class="flex-col">
          <label for="page"> Page: </label>
          <input
            v-model="page"
            id="page"
            type="number"
            placeholder="Page number"
          />
        </div>
        <div v-if="isOnVectorRoute" class="flex-col">
          <label for="topK"> topK: </label>
          <input v-model="topK" id="topK" type="number" placeholder="topK" />
        </div>
        <div v-if="isOnVectorRoute" class="flex-col">
          <label for="items"> Items: </label>
          <input
            v-model="items"
            id="items"
            type="number"
            placeholder="Items per page"
          />
        </div>
        <div v-if="isOnVectorRoute" class="flex-col">
          <label for="union"> Union: </label>
          <input v-model="union" id="union" type="number" placeholder="Union" />
        </div>
        <div class="flex-col">
          <label for="algo">AB Algo:</label>
          <select v-model="algo" id="algo">
            <option v-for="algo in algoOptions" :key="algo" :value="algo">
              {{ algo }}
            </option>
          </select>
        </div>
        <div class="flex">
          <label for="debugMode"> Debug: </label>
          <input v-model="debugMode" id="debugMode" type="checkbox" />
        </div>
        <div class="flex">
          <label for="audit"> Audit: </label>
          <input
            v-model="auditMode"
            id="audit"
            type="checkbox"
            :disabled="!auditorEmail"
            @change="pushToAuditPage"
          />
        </div>
      </div>
    </section>
    <section class="advanced-filters">
      <div class="flex">
        <label for="isLexical"> Lexical Search: </label>
        <input v-model="isLexicalSearch" id="isLexical" type="checkbox" />
      </div>
      <div class="flex">
        <label for="isHybrid"> Hybrid Search: </label>
        <input v-model="isHybridSearch" id="isHybrid" type="checkbox" />
      </div>
    </section>
    <section class="products-container">
      <div class="wrapper">
        <div v-if="lexicalCallDone" class="flex-col">
          {{ lexicalHeading }}
          <div v-if="auditMode" class="audit-header">
            <div class="flex">
              <label for="markAllRelevantLexical"> Mark All Relevant: </label>
              <input
                v-model="markAllRelevantLexical"
                id="markAllRelevantLexical"
                type="checkbox"
              />
            </div>
            <button @click="() => submitAudit('LEXICAL')" class="button">
              Submit Lexical Audit
            </button>
          </div>
        </div>
        <div v-if="isLexicalSearch" class="products lexical">
          <div
            v-for="(product, index) in lexicalProducts"
            :key="index"
            class="product"
          >
            <div class="card-meta">
              <p class="rank">Rank: {{ product.position }}</p>
              <p v-if="product.tag" class="tag" :id="product.tag">
                {{
                  product.tag === "TRENDING"
                    ? "Paling top"
                    : product.tag === "MANUAL_MERCHANDISED"
                    ? "Pilihan Blibli"
                    : ""
                }}
              </p>
            </div>
            <img :src="product.image" @click="goToPDP(product.url)" />
            <p class="product-name">
              {{ product.name }}
            </p>
            <p class="product-sku">
              <strong>{{ product.sku }}</strong>
            </p>
            <p v-if="product.score">
              Score: <span class="score">{{ product.score }}</span>
            </p>
            <p v-if="product.vectorBoost">
              Vector Boost:
              <span class="v-score">{{ product.vectorBoost }}</span>
            </p>
            <div v-if="auditMode" class="flex-40">
              <label :for="'isRelevantLexical' + index"> Relevant: </label>
              <input
                v-model="product.relevance"
                :id="'isRelevantLexical' + index"
                type="checkbox"
              />
            </div>
            <div v-if="auditMode" class="flex-col">
              <textarea
                v-model="product.comment"
                :id="'commentLexical' + index"
                rows="4"
                cols="50"
                placeholder="Enter comments"
              />
            </div>
          </div>
        </div>
      </div>
      <div class="wrapper">
        <div v-if="hybridCallDone" class="flex-col">
          {{ hybridHeading }}
          <div v-if="auditMode" class="audit-header">
            <div class="flex">
              <label for="markAllRelevantHybrid"> Mark All Relevant: </label>
              <input
                v-model="markAllRelevantHybrid"
                id="markAllRelevantHybrid"
                type="checkbox"
              />
            </div>
            <button @click="() => submitAudit('HYBRID')" class="button">
              Submit Hybrid Audit
            </button>
          </div>
        </div>
        <div v-if="isHybridSearch" class="products hybrid">
          <div
            v-for="(product, index) in hybridProducts"
            :key="index"
            class="product"
          >
            <div class="card-meta">
              <p class="rank">Rank: {{ product.position }}</p>
              <p v-if="product.tag" class="tag" :id="product.tag">
                {{
                  product.tag === "TRENDING"
                    ? "Paling top"
                    : product.tag === "MANUAL_MERCHANDISED"
                    ? "Pilihan Blibli"
                    : ""
                }}
              </p>
            </div>
            <img :src="product.image" @click="goToPDP(product.url)" />
            <p class="product-name">
              {{ product.name }}
            </p>
            <p class="product-sku">
              <strong>{{ product.sku }}</strong>
            </p>
            <p v-if="product.score">
              Score: <span class="score">{{ product.score }}</span>
            </p>
            <p v-if="product.vectorBoost">
              Vector score:
              <span class="v-score">{{ product.vectorBoost }}</span>
            </p>
            <div v-if="auditMode" class="flex-40">
              <label :for="'isRelevantHybrid' + index"> Relevant: </label>
              <input
                v-model="product.relevance"
                :id="'isRelevantHybrid' + index"
                type="checkbox"
              />
            </div>
            <div v-if="auditMode" class="flex-col">
              <!-- <label :for="'commentHybrid' + index"> Comment: </label> -->
              <textarea
                v-model="product.comment"
                :id="'commentHybrid' + index"
                rows="4"
                cols="50"
                placeholder="Enter comments"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
* {
  outline: none;
  font-family: Source Sans Pro, sans-serif;
}
*:focus {
  outline: none;
}
.container {
  padding: 0px 80px;
  margin-top: 14px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
.filter-input {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  gap: 16px;
}
.filters,
.advanced-filters,
.products,
.products-container {
  align-items: center;
  width: 100%;
  display: flex;
  gap: 16px;
}
.products {
  flex-wrap: wrap;
}
.advanced-filters,
.products-container {
  margin: 24px 0px;
  justify-content: space-between;
  align-items: flex-start;
}
.advanced-filters > .flex,
.products-container > .products {
  width: calc(50% - 8px);
}
.wrapper {
  width: calc(50% - 8px);
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 40px;
}
.flex {
  display: flex;
  align-items: center;
  min-height: 100%;
}
.flex-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}
input[type="text"] {
  height: 32px;
  border-radius: 4px;
  background-color: rgb(240, 242, 246);
  padding: 0px 8px;
  box-sizing: border-box;
  border: rgb(240, 242, 246);
  width: 500px;
}
input[type="number"] {
  height: 32px;
  width: 80px;
  border-radius: 4px;
  background-color: rgb(240, 242, 246);
  padding: 0px 8px;
  box-sizing: border-box;
  border: rgb(240, 242, 246);
}
select {
  height: 32px;
  width: 100px;
  border-radius: 4px;
  background-color: rgb(240, 242, 246);
  padding: 0px 8px;
  box-sizing: border-box;
  border: rgb(240, 242, 246);
  border-right: 16px solid transparent;
}
input[type="checkbox"] {
  position: relative;
  border: 2px solid #0072ff;
  border-radius: 2px;
  background: none;
  cursor: pointer;
  line-height: 0;
  margin: 0 0.6em;
  outline: 0;
  padding: 0 !important;
  vertical-align: text-top;
  height: 20px;
  width: 20px;
  -webkit-appearance: none;
  opacity: 0.5;
}
input[type="checkbox"]:hover {
  opacity: 1;
}
input[type="checkbox"]:checked {
  background-color: #0072ff;
  opacity: 1;
}
input[type="checkbox"]:before {
  content: "";
  position: absolute;
  right: 50%;
  top: 50%;
  width: 4px;
  height: 10px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  margin: -1px -1px 0 -1px;
  transform: rotate(45deg) translate(-50%, -50%);
  z-index: 2;
}
input[type="checkbox"]:disabled {
  color: gray;
  border: solid gray;
  cursor: not-allowed;
}
.product {
  width: calc((100% - 132px) / 3);
  border: 1px solid rgb(240, 242, 246);
  border-radius: 8px;
  overflow: hidden;
  box-sizing: border-box;
  padding: 0px 4px;
}
.product > img {
  width: 100%;
  aspect-ratio: 1/1;
  cursor: pointer;
}
.product-name {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}
p {
  margin: 10px 0px;
}
.score {
  color: rgb(9, 171, 59);
  font-size: 12px;
  font-weight: 500;
}
.v-score {
  color: rgb(246, 51, 102);
  font-size: 12px;
  font-weight: 600;
}
span {
  background-color: rgb(240, 242, 246);
  padding: 4px;
  border-radius: 4px;
}
.flex-40 {
  display: flex;
  align-items: center;
  height: 40px;
}
textarea {
  padding: 12px 8px;
  box-sizing: border-box;
  border-radius: 6px;
}
.filters {
  justify-content: space-between;
}
button {
  cursor: pointer;
  display: inline-flex;
  -webkit-box-align: center;
  align-items: center;
  -webkit-box-pack: center;
  justify-content: center;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  min-height: 38.4px;
  margin: 0px;
  line-height: 1.6;
  color: inherit;
  width: auto;
  background-color: rgb(255, 255, 255);
  border: 1px solid rgba(49, 51, 63, 0.2);
}
.audit-header {
  display: flex;
  flex-direction: rows;
  justify-content: space-between;
  align-items: flex-start;
  max-width: calc(100% - 104px);
}
.card-meta {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 10px 4px 4px 4px;
}
.card-meta > .tag {
  margin: 0px;

  padding: 2px 4px;
  color: white;
  border-radius: 4px;
  font-size: 11px;
}
#TRENDING {
  background-color: #fe9a36;
}
#MANUAL_MERCHANDISED {
  background-color: #09acde;
}

.card-meta > .rank {
  margin: 0px;
  border-radius: 4px;
  font-size: 13px;
}
#userEmail {
  background-color: #fff;
}
.auditor-email {
  margin-right: auto;
  display: flex;
}

.clear-icon {
  cursor: pointer;
  margin-left: 10px;
  color: blue; /* You can change the color to your preference */
}

.clear-icon:hover {
  text-decoration: underline;
}
</style>
