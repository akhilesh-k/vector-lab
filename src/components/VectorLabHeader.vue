<script setup>
import { ref, watch, computed } from "vue";
import Logo from "../assets/logo.svg";
const emailInput = ref("");
const auditorEmail = ref(localStorage.getItem("auditorEmail") || "");

const saveAuditorEmail = () => {
  const enteredEmail = emailInput.value.trim();
  if (enteredEmail && enteredEmail.endsWith("@gdn-commerce.com")) {
    localStorage.setItem("auditorEmail", enteredEmail);
    auditorEmail.value = enteredEmail;
  } else {
    auditorEmail.value = "";
    emailInput.value = "";
  }
};
</script>
<template>
  <main class="container">
    <div class="flex-col auditor-email">
      <template v-if="!auditorEmail">
        <input
          v-model="emailInput"
          id="userEmail"
          type="text"
          placeholder="Please enter your GDN email and press Enter to start auditing..."
          @keypress.enter="saveAuditorEmail"
        />
      </template>
      <template v-else>
        <p>Hi, {{ auditorEmail }}</p>
      </template>
    </div>
    <div class="heading">
      <h1>Blibli Vector Lab ⚡</h1>
      <img :src="Logo" />
    </div>
  </main>
</template>

<style scoped>
.container {
  padding: 0px 80px;
  margin-top: 24px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.heading {
  font-size: 20px;
  margin: 10px 0;
  display: flex;
  align-items: center;
  max-width: 90%;
  justify-content: space-between;
}
.auditor-email {
  margin-right: auto;
  display: flex;
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
</style>
