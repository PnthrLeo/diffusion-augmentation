import { $el } from "../../../../scripts/ui.js";
import { addStylesheet, getUrl, loadImage } from "./utils.js";
import { createSpinner } from "./spinner.js";

addStylesheet(getUrl("lightbox.css", import.meta.url));

const $$el = (tag, name, ...args) => {
	if (name) name = "-" + name;
	return $el(tag + ".pysssss-lightbox" + name, ...args);
};

const ani = async (a, t, b) => {
	a();
	await new Promise((r) => setTimeout(r, t));
	b();
};

export class Lightbox {
	constructor() {
		this.el = $$el("div", "", {
			parent: document.body,
			onclick: (e) => {
				e.stopImmediatePropagation();
				this.close();
			},
			style: {
				display: "none",
				opacity: 0,
			},
		});
		this.closeBtn = $$el("div", "close", {
			parent: this.el,
		});
		this.prev = $$el("div", "prev", {
			parent: this.el,
			onclick: (e) => {
				this.update(-1);
				e.stopImmediatePropagation();
			},
		});
		this.main = $$el("div", "main", {
			parent: this.el,
		});
		this.next = $$el("div", "next", {
			parent: this.el,
			onclick: (e) => {
				this.update(1);
				e.stopImmediatePropagation();
			},
		});
		this.link = $$el("a", "link", {
			parent: this.main,
			target: "_blank",
		});
		this.spinner = createSpinner();
		this.link.appendChild(this.spinner);
		this.img = $$el("img", "img", {
			style: {
				opacity: 0,
			},
			parent: this.link,
			onclick: (e) => {
				e.stopImmediatePropagation();
			},
		});
	}

	close() {
		ani(
			() => (this.el.style.opacity = 0),
			200,
			() => (this.el.style.display = "none")
		);
	}

	async show(images, index) {
		this.images = images;
		this.index = index || 0;
		await this.update(0);
	}

	async update(shift) {
		this.index += shift;

		this.prev.style.visibility = this.index ? "unset" : "hidden";
		this.next.style.visibility = this.index === this.images.length - 1 ? "hidden" : "unset";

		const img = this.images[this.index];
		this.el.style.display = "flex";
		this.el.clientWidth; // Force a reflow
		this.el.style.opacity = 1;
		this.img.style.opacity = 0;
		this.spinner.style.display = "inline-block";
		await loadImage(img);
		this.spinner.style.display = "none";
		this.link.href = img;
		this.img.src = img;
		this.img.style.opacity = 1;
	}
}

export const lightbox = new Lightbox();
