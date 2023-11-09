<script setup>
import { onBeforeMount, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import SidebarLogoOpen from "../assets/icons/sidebar-open.svg";
import SidebarLogoClose from "../assets/icons/sidebar-close.svg";
import BlibliHalfLogo from "../assets/icons/blibli-half-logo.png";
const router = useRouter();
const auditorEmail = ref(localStorage.getItem("auditorEmail") || "");
const sideBar = ref();
const sideBarLogo = ref();

const isCollapsed = ref(true);

// Function to toggle the sidebar's collapsed state
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};
const navigateTo = (url) => {
  router.push(url);
  isCollapsed.value = !isCollapsed.value;
};

const collapseWhenClickedOutside = (event) => {
  if (
    sideBar.value &&
    !sideBar.value.contains(event.target) &&
    event.target !== sideBarLogo.value
  ) {
    isCollapsed.value = true;
  }
};
const sideBarUrls = [
  { name: "Vector Search", url: "vector-search" },
  { name: "Perform Audit", url: "audit" },
  { name: "Audit History", url: "audit-history" },
  { name: "Configure", url: "configure" },
  { name: "Release Notes", url: "release-notes" },
];
const convertEmailToName = (email) => {
  const parts = email.split("@")[0].split(".");
  return parts
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
};
onMounted(() => {
  window.addEventListener("click", collapseWhenClickedOutside);
});
onBeforeUnmount(() => {
  window.removeEventListener("click", collapseWhenClickedOutside);
});
</script>

<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }" ref="sideBar">
    <div class="sidebar-header">
      <img
        v-if="!isCollapsed"
        @click="toggleSidebar"
        class="sidebar-btn"
        :src="BlibliHalfLogo"
      />
      <p v-if="!isCollapsed">Vector Lab</p>
      <img
        v-if="!isCollapsed"
        @click.stop="toggleSidebar"
        class="sidebar-btn"
        :src="SidebarLogoClose"
      />
      <img
        v-else
        ref="sideBarLogo"
        @click.stop="toggleSidebar"
        class="sidebar-btn"
        :src="SidebarLogoOpen"
      />
    </div>

    <div v-show="!isCollapsed" class="content">
      <div v-for="(item, index) in sideBarUrls" :key="index">
        <p class="content-item" @click="navigateTo(item.url)">
          {{ item.name }}
        </p>
      </div>
    </div>
    <footer class="sidebar-footer" v-show="!isCollapsed">
      <span v-if="auditorEmail">Hi {{ convertEmailToName(auditorEmail) }}</span>
      <span>Vector Lab v1.2.0</span>
    </footer>
  </div>
</template>

<style scoped>
.sidebar {
  z-index: 1;
  background-color: #fff;
  width: 200px;
  height: 100%;
  border-right: solid 1px rgb(240, 242, 246);
  box-shadow: 1px 0 2px rgba(0, 0, 0, 0.2);
  transition: width 0.4s ease, transform 0.4s ease 0.5s; /* Add transition for width and a delayed transition for transform */
  position: fixed;
  top: 0;
  left: 0;
}
.sidebar:not(.collapsed) {
  width: 200px;
  transform: translateX(0); /* Slide in from the left */
  transition-delay: 0s, 0s; /* Reset transition delays */
}

/* When collapsed */
.sidebar.collapsed {
  width: 50px;
}

.collapsed {
  width: 50px;
}

.sidebar-btn {
  display: block;
  margin: 10px;
  cursor: pointer;
  width: 32px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content {
  padding: 20px;
  transition: width 2s ease, transform 2s ease 0.5s;
}

.content-item {
  background-color: rgb(246, 246, 247);
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 400;
}
.sidebar-footer {
  padding: 20px;
  flex: 0; /* Push to the bottom */
  display: flex;
  position: fixed;
  bottom: 0;
  flex-direction: column;
  gap: 24px;
}

.sidebar-footer span {
  font-weight: 400;
  color: grey;
}
</style>
