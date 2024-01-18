<script setup>
import FileUploadIcon from "../assets/icons/file-upload.svg";
import CheckmarkIcon from "../assets/icons/checkmark.svg";
import ExcelJS from "exceljs";
import { ref } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();
const uploadedFile = ref(null);
const uploadedFileName = ref(null);
const fileUploaded = ref(false);
const errorMessage = ref(null);
const searchKeywords = ref([]);
const searchLoads = ref([]);
const searchClicks = ref([]);
const ctr = ref([]);
const c1CategoryCode = ref([]);
const c2CategoryCode = ref([]);
const c3CategoryCode = ref([]);
const c3Name = ref([]);
const c3Category = ref([]);
const auditors = ref([]);
const ifDataVerified = ref(false);
const auditorEmail = ref(localStorage.getItem("auditorEmail"));

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
    c1CategoryCode: c1CategoryCode.value[index],
    searchLoads: searchLoads.value[index],
    searchClicks: searchClicks.value[index],
    ctr: ctr.value[index],
    c1CategoryCode: c1CategoryCode.value[index],
    c2CategoryCode: c2CategoryCode.value[index],
    c3CategoryCode: c3CategoryCode.value[index],
    c3Name: c3Name.value[index],
    c3Category: c3Category.value[index],
  }));
};

const uploadVerifiedAuditCampaign = async () => {
  try {
    const formData = new FormData();
    formData.append("file", uploadedFile.value);
    formData.append("campaignOwner", auditorEmail.value);

    const response = await fetch(
      "http://xsearch-solr-vector-2.qa2-sg.cld:5000/upload-audit-assignment",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error:", errorData.error);
    } else {
      const responseData = await response.json();
      ifDataVerified.value = !ifDataVerified.value;
    }
  } catch (error) {
    console.error("Fetch Error:", error);
  }
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
    const sheet = workbook.getWorksheet("Audit");

    const data = [];
    sheet.eachRow((row, rowNumber) => {
      if (rowNumber !== 1) {
        const rowData = {
          search_internal_keyword: row.getCell(1).value,
          search_loads: row.getCell(2).value,
          search_clicks: row.getCell(3).value,
          ctr: row.getCell(4).value,
          c1CategoryCode: row.getCell(5).value,
          c2CategoryCode: row.getCell(6).value,
          c3CategoryCode: row.getCell(7).value,
          c3_name: row.getCell(8).value,
          c3_category: row.getCell(9).value,
          auditors: row.getCell(10).value,
        };
        data.push(rowData);

        if (rowData.search_internal_keyword !== null) {
          searchKeywords.value.push(rowData.search_internal_keyword);
          searchLoads.value.push(rowData.search_loads);
          searchClicks.value.push(rowData.search_clicks);
          ctr.value.push(rowData.ctr);
          c1CategoryCode.value.push(rowData.c1CategoryCode);
          c2CategoryCode.value.push(rowData.c2CategoryCode);
          c3CategoryCode.value.push(rowData.c3CategoryCode);
          c3Name.value.push(rowData.c3_name);
          c3Category.value.push(rowData.c3_category);
        }
        if (rowData.auditors !== null) {
          if (
            typeof rowData.auditors === "object" ||
            rowData.auditors instanceof Object
          ) {
            auditors.value.push(rowData.auditors.text);
          } else {
            auditors.value.push(rowData.auditors);
          }
        }
      }
    });
    getRandomSearchTerms();
    uploadedFile.value = file;
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
    <section v-show="!fileUploaded" class="upload-section">
      <h1>Upload file</h1>
      <h3 style="color: #8e7cc4; margin-top: 0; font-weight: 400">
        Upload the document containing Search terms and Auditors
      </h3>
      <a style="padding-bottom: 8px" href="/search-audit.xlsx" download
        >File Template</a
      >

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
    <div v-if="fileUploaded && !ifDataVerified" class="file-read">
      <div class="upload-alert">
        <h3>File read successfully</h3>
        <img :src="CheckmarkIcon" alt="" class="icon" />
      </div>
      <p style="color: #8e7cc4; font-weight: 600">{{ uploadedFileName }}</p>
    </div>
    <section v-if="!ifDataVerified">
      <div
        v-if="searchKeywords.length && randomSearchTerms"
        class="verification-bar"
        style="background-color: orange"
      >
        <div class="verification-msg">
          <h4 v-if="searchKeywords.length && randomSearchTerms">
            Verify your data before submitting:
          </h4>
          <span v-if="searchKeywords.length && randomSearchTerms"
            >Scroll to the bottom to submit the verification</span
          >
        </div>
      </div>
      <div
        v-if="searchKeywords.length && randomSearchTerms.length"
        class="data-verification-stage"
      >
        <div class="checklist-section">
          <div class="checklist">
            <img :src="CheckmarkIcon" alt="" class="icon" />
            <h3>Match the search terms and their Index in the excel sheet</h3>
          </div>

          <table>
            <thead>
              <tr>
                <th>Idx</th>
                <th>Search Term</th>
                <th>Search Loads</th>
                <th>Search Clicks</th>
                <th>CTR</th>
                <th>C1 Category Code</th>
                <th>C2 Category Code</th>
                <th>C3 Category Code</th>
                <th>C3 Name</th>
                <th>C3 Category</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="randomSearchTerm in randomSearchTerms"
                :key="randomSearchTerm.index"
              >
                <td>{{ randomSearchTerm.index }}</td>
                <td>{{ randomSearchTerm.searchTerm }}</td>
                <td>{{ randomSearchTerm.searchLoads }}</td>
                <td>{{ randomSearchTerm.searchClicks }}</td>
                <td>{{ randomSearchTerm.ctr }}</td>
                <td>{{ randomSearchTerm.c1CategoryCode }}</td>
                <td>{{ randomSearchTerm.c2CategoryCode }}</td>
                <td>{{ randomSearchTerm.c3CategoryCode }}</td>
                <td>{{ randomSearchTerm.c3Name }}</td>
                <td>{{ randomSearchTerm.c3Category }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="checklist-section">
          <div class="checklist">
            <img :src="CheckmarkIcon" alt="" class="icon" />
            <h3>Auditor list</h3>
          </div>

          <table>
            <thead>
              <tr>
                <th>Auditor</th>
                <th>Auditor Email</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="auditor in auditors" :key="auditor">
                <td>{{ convertEmailToName(auditor) }}</td>
                <td>{{ auditor }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div
        v-if="searchKeywords.length && randomSearchTerms"
        class="verification-bar"
        style="background-color: #00c04b"
      >
        <div class="verification-msg">
          <h4 v-if="searchKeywords.length && randomSearchTerms">
            If all looks good in the tables above, click on verify to submit the
            data
          </h4>
          <span v-if="searchKeywords.length && randomSearchTerms"
            >Clicking on verify will submit the audit assignment file</span
          >
        </div>
        <button
          v-if="
            searchKeywords.length && randomSearchTerms.length && !ifDataVerified
          "
          style="background-color: green"
          @click="uploadVerifiedAuditCampaign"
        >
          Verify
        </button>
      </div>
    </section>
    <section
      v-if="ifDataVerified"
      class="verification-bar"
      style="background-color: #0072ff"
    >
      <div>
        <h3>Thank you for submitting</h3>
        <span>The audit campaign has been created</span>
      </div>
      <button
        style="background-color: white; color: black"
        @click="router.push('/audit-history')"
      >
        Go back to Audit History
      </button>
    </section>
  </main>
</template>

<style scoped>
.container {
  padding: 0px 80px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  margin-bottom: 80px;
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
  gap: 8px;
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
.data-verification-stage {
  display: flex;
  flex-direction: column;
}
.checklist-section {
  display: flex;
  flex-direction: column;
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
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

td,
th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

th {
  background-color: #f2f2f2;
}
.verification-bar {
  margin: 32px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  border-radius: 16px;
  padding: 8px 16px 24px;
  span {
    font-size: 13px;
    font-weight: 400;
  }
}
</style>
