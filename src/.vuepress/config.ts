import { defineUserConfig } from "vuepress";
import theme from "./theme.js";

export default defineUserConfig({
  base: "/",

  lang: "zh-CN",
  title: "LX Music Api Server",
  description: "适用于 LX Music 的解析接口服务器的 Python 实现",

  theme,

  // 和 PWA 一起启用
  // shouldPrefetch: false,
});
