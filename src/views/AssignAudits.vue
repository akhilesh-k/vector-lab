<script setup>
import FileUploadIcon from "../assets/icons/file-upload.svg";
import CheckmarkIcon from "../assets/icons/checkmark.svg";
import ExcelJS from "exceljs";
import { ref } from "vue";

const uploadedFileName = ref(null);
const fileUploaded = ref(false);
const errorMessage = ref(null);
const searchKeywords = ref([]);
const auditors = ref([]);
const ifDataVerified = ref(false);

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    handleFile(file);
  }
};

const convertEmailToName = (email) => {
  const parts = email.split("@")[0].split(".");
  return parts
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
};
const handleDrop = (event) => {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file) {
    handleFile(file);
  }
};
const randomSearchTerms = ref([]);
const getRandomSearchTerms = () => {
  const totalSearchTerms = searchKeywords.value.length;
  const randomIndexes = Array.from({ length: 10 }, () =>
    Math.floor(Math.random() * totalSearchTerms)
  );
  randomSearchTerms.value = randomIndexes.map((index) => ({
    index: index + 2,
    searchTerm: searchKeywords.value[index],
  }));
};

const handleFile = async (file) => {
  // if (
  //   file.type !== "application/vnd.ms-excel" ||
  //   file.type !=
  //     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  // ) {
  //   errorMessage.value = "Invalid file type. Please upload an XLS file.";
  //   return;
  // }

  try {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.load(file);

    // Assuming the first sheet is named "Assignment"
    const sheet = workbook.getWorksheet("Assignment");

    const data = [];
    sheet.eachRow((row, rowNumber) => {
      if (rowNumber !== 1) {
        // Skip the first row (header row)
        const rowData = {
          search_internal_keyword: row.getCell(1).value,
          auditors: row.getCell(2).value,
        };
        data.push(rowData);

        if (rowData.search_internal_keyword !== null) {
          searchKeywords.value.push(rowData.search_internal_keyword);
        }
        if (rowData.auditors !== null) {
          auditors.value.push(rowData.auditors);
        }
      }
    });
    getRandomSearchTerms();
    uploadedFileName.value = file.name;
    errorMessage.value = null;
    fileUploaded.value = true;
  } catch (error) {
    errorMessage.value = "Error reading the Excel file.";
    console.error(error);
  }
};
</script>

<template>
  <main class="container">
    <h3 style="color: red">
      Assign Audits - This is work in progress. Please avoid using this tab.
    </h3>
    <section v-show="!fileUploaded" class="upload-section">
      <h1>Upload file</h1>
      <h3 style="color: #8e7cc4; margin-top: 0; font-weight: 400">
        Upload the document containing Search terms and Auditors
      </h3>
      <div @dragover.prevent @drop.prevent="handleDrop" class="upload-area">
        <img :src="FileUploadIcon" style="width: 64px" alt="" />
        <div v-if="!uploadedFileName" class="upload-details">
          <p style="color: #8e7cc4">Drag and drop file here</p>
          <p style="color: #8e7cc4">-OR-</p>
          <button @click="$refs.fileInput.click()">Browse Files</button>
        </div>
        <input
          type="file"
          accept=".xls,.xlsx"
          ref="fileInput"
          @change="handleFileSelect"
          style="display: none"
        />
      </div>
    </section>
    <div v-if="fileUploaded" class="file-read">
      <div class="upload-alert">
        <p>File read successfully</p>
      </div>
      <p>{{ uploadedFileName }}</p>
    </div>
    <section v-if="!ifDataVerified">
      <h4 v-if="searchKeywords.length && randomSearchTerms">
        Verify your data before submitting:
      </h4>
      <button
        v-if="searchKeywords.length && randomSearchTerm && !ifDataVerified"
        style="background-color: green"
        @click="ifDataVerified = !ifDataVerified"
      >
        Verify
      </button>
      <div
        v-if="searchKeywords.length && randomSearchTerms"
        class="data-verification-stage"
      >
        <div>
          <div class="checklist">
            <img :src="CheckmarkIcon" alt="" class="icon" />
            <p>Checklist 1</p>
          </div>
          <p>Match the search terms and their Index in the excel sheet</p>
          <div
            v-for="randomSearchTerm in randomSearchTerms"
            :key="randomSearchTerm"
          >
            {{ randomSearchTerm.index }}
            {{ randomSearchTerm.searchTerm }}
          </div>
        </div>
        <div>
          <div class="checklist">
            <img :src="CheckmarkIcon" alt="" class="icon" />
            <p>Checklist 2</p>
          </div>
          <p>Match the Auditor list</p>
          <div v-for="auditor in auditors" :key="auditor">
            {{ convertEmailToName(auditor) }}
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.container {
  padding: 0px 80px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
.file-read {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: flex-start;
  border: 1px dashed #8e7cc4;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  box-sizing: border-box;
}
.upload-alert {
  display: flex;
  align-items: center;
}
.upload-section {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: center;
  justify-content: space-around;
  box-sizing: border-box;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px dashed #8e7cc4;
  border-radius: 16px;
  padding: 36px;
  text-align: center;
  cursor: pointer;
  width: 50%;
  box-sizing: border-box;
}

.error-message {
  color: red;
}
button {
  background-color: #25008d;
  color: #fff;
  border-radius: 8px;
  padding: 12px 36px;
  cursor: pointer;
  border: none;
}
.icon {
  width: 24px;
}
.checklist {
  display: flex;
  gap: 4px;
}
.data-verification-stage {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}
</style>
