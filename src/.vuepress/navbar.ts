import { navbar } from "vuepress-theme-hope";

const NavbarConfig = navbar([
    {
        text: "首页",
        link: "/README.md",
        icon: "home",
    },
    { text: "介绍", link: "/guide/README.md", icon: "fas fa-info" },
    {
        text: "部署",
        link: "/deploy/README.md",
        icon: "fas fa-file-alt",
    },
]);

export default NavbarConfig