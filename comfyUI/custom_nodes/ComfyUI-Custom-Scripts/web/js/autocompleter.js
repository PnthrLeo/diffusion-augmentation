import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";
import { api } from "../../../../scripts/api.js";
import { $el, ComfyDialog } from "../../../../scripts/ui.js";
import { TextAreaAutoComplete } from "./common/autocomplete.js";
import { ModelInfoDialog } from "./common/modelInfoDialog.js";

function parseCSV(csvText) {
	const rows = [];
	const delimiter = ",";
	const quote = '"';
	let currentField = "";
	let inQuotedField = false;

	function pushField() {
		rows[rows.length - 1].push(currentField);
		currentField = "";
		inQuotedField = false;
	}

	rows.push([]); // Initialize the first row

	for (let i = 0; i < csvText.length; i++) {
		const char = csvText[i];
		const nextChar = csvText[i + 1];

		if (!inQuotedField) {
			if (char === quote) {
				inQuotedField = true;
			} else if (char === delimiter) {
				pushField();
			} else if (char === "\r" || char === "\n" || i === csvText.length - 1) {
				pushField();
				if (nextChar === "\n") {
					i++; // Handle Windows line endings (\r\n)
				}
				rows.push([]); // Start a new row
			} else {
				currentField += char;
			}
		} else {
			if (char === quote && nextChar === quote) {
				currentField += quote;
				i++; // Skip the next quote
			} else if (char === quote) {
				inQuotedField = false;
			} else {
				currentField += char;
			}
		}
	}

	if (currentField || csvText[csvText.length - 1] === ",") {
		pushField();
	}

	// Remove the last row if it's empty
	if (rows[rows.length - 1].length === 0) {
		rows.pop();
	}

	return rows;
}

async function getCustomWords() {
	const resp = await api.fetchApi("/pysssss/autocomplete", { cache: "no-store" });
	if (resp.status === 200) {
		return await resp.text();
	}
	return undefined;
}

async function addCustomWords(text) {
	if (!text) {
		text = await getCustomWords();
	}
	if (text) {
		TextAreaAutoComplete.updateWords(
			"pysssss.customwords",
			parseCSV(text).reduce((p, n) => {
				let text;
				let priority;
				let value;
				let num;
				switch (n.length) {
					case 0:
						return;
					case 1:
						// Single word
						text = n[0];
						break;
					case 2:
						// Word,[priority|alias]
						num = +n[1];
						if (isNaN(num)) {
							text = n[1];
							value = n[0];
						} else {
							text = n[0];
							priority = num;
						}
						break;
					case 4:
						// a1111 csv format?
						value = n[0];
						priority = +n[2];
						const aliases = n[3];
						if (aliases) {
							const split = aliases.split(",");
							for (const text of split) {
								p[text] = { text, priority, value };
							}
						}
						text = value;
					default:
						// Word,alias,priority
						text = n[1];
						value = n[0];
						priority = +n[2];
						break;
				}
				p[text] = { text, priority, value };
				return p;
			}, {})
		);
	}
}

class EmbeddingInfoDialog extends ModelInfoDialog {
	async addInfo() {
		super.addInfo();
		const info = await this.addCivitaiInfo();
		if (info) {
			$el("div", {
				parent: this.content,
				innerHTML: info.description,
				style: {
					maxHeight: "250px",
					overflow: "auto",
				},
			});
		}
	}
}

class CustomWordsDialog extends ComfyDialog {
	async show() {
		const text = await getCustomWords();
		this.words = $el("textarea", {
			textContent: text,
			style: {
				width: "70vw",
				height: "70vh",
			},
		});

		const input = $el("input", {
			style: {
				flex: "auto",
			},
			value:
				"https://gist.githubusercontent.com/pythongosssss/1d3efa6050356a08cea975183088159a/raw/a18fb2f94f9156cf4476b0c24a09544d6c0baec6/danbooru-tags.txt",
		});

		super.show(
			$el(
				"div",
				{
					style: {
						display: "flex",
						flexDirection: "column",
						overflow: "hidden",
						maxHeight: "100%",
					},
				},
				[
					$el("h2", {
						textContent: "Custom Autocomplete Words",
						style: {
							color: "#fff",
							marginTop: 0,
							textAlign: "center",
							fontFamily: "sans-serif",
						},
					}),
					$el(
						"div",
						{
							style: {
								color: "#fff",
								fontFamily: "sans-serif",
								display: "flex",
								alignItems: "center",
								gap: "5px",
							},
						},
						[
							$el("label", { textContent: "Load Custom List: " }),
							input,
							$el("button", {
								textContent: "Load",
								onclick: async () => {
									try {
										const res = await fetch(input.value);
										if (res.status !== 200) {
											throw new Error("Error loading: " + res.status + " " + res.statusText);
										}
										this.words.value = await res.text();
									} catch (error) {
										alert("Error loading custom list, try manually copy + pasting the list");
									}
								},
							}),
						]
					),
					this.words,
				]
			)
		);
	}

	createButtons() {
		const btns = super.createButtons();
		const save = $el("button", {
			type: "button",
			textContent: "Save",
			onclick: async (e) => {
				try {
					const res = await api.fetchApi("/pysssss/autocomplete", { method: "POST", body: this.words.value });
					if (res.status !== 200) {
						throw new Error("Error saving: " + res.status + " " + res.statusText);
					}
					save.textContent = "Saved!";
					addCustomWords(this.words.value);
					setTimeout(() => {
						save.textContent = "Save";
					}, 500);
				} catch (error) {
					alert("Error saving word list!");
					console.error(error);
				}
			},
		});

		btns.unshift(save);
		return btns;
	}
}

const id = "pysssss.AutoCompleter";

app.registerExtension({
	name: id,
	init() {
		async function addEmbeddings() {
			const embeddings = await api.getEmbeddings();
			const words = {};
			words["embedding:"] = { text: "embedding:" };

			for (const emb of embeddings) {
				const v = `embedding:${emb}`;
				words[v] = {
					text: v,
					info: () => new EmbeddingInfoDialog(emb).show("embeddings", emb),
				};
			}

			TextAreaAutoComplete.updateWords("pysssss.embeddings", words);
		}

		Promise.all([addEmbeddings(), addCustomWords()]);

		const STRING = ComfyWidgets.STRING;
		const SKIP_WIDGETS = new Set(["ttN xyPlot.x_values", "ttN xyPlot.y_values"]);
		ComfyWidgets.STRING = function (node, inputName, inputData) {
			const r = STRING.apply(this, arguments);

			if (inputData[1]?.multiline) {
				// Disabled on this input
				const config = inputData[1]?.["pysssss.autocomplete"];
				if (config === false) return r;

				// In list of widgets to skip
				const id = `${node.comfyClass}.${inputName}`;
				if (SKIP_WIDGETS.has(id)) return r;

				let words;
				let separator;
				if (typeof config === "object") {
					separator = config.separator;
					words = {};
					if (config.words) {
						// Custom wordlist, this will have been registered on setup
						Object.assign(words, TextAreaAutoComplete.groups[node.comfyClass + "." + inputName] ?? {});
					}

					for (const item of config.groups ?? []) {
						if (item === "*") {
							// This widget wants all global words included
							Object.assign(words, TextAreaAutoComplete.globalWords);
						} else {
							// This widget wants a specific group included
							Object.assign(words, TextAreaAutoComplete.groups[item] ?? {});
						}
					}
				}

				new TextAreaAutoComplete(r.widget.inputEl, words, separator);
			}

			return r;
		};

		TextAreaAutoComplete.globalSeparator = localStorage.getItem(id + ".AutoSeparate") ?? ", ";
		app.ui.settings.addSetting({
			id,
			name: "🐍 Text Autocomplete",
			defaultValue: true,
			type: (name, setter, value) => {
				return $el("tr", [
					$el("td", [
						$el("label", {
							for: id.replaceAll(".", "-"),
							textContent: name,
						}),
					]),
					$el("td", [
						$el(
							"label",
							{
								textContent: "Enabled ",
								style: {
									display: "block",
								},
							},
							[
								$el("input", {
									id: id.replaceAll(".", "-"),
									type: "checkbox",
									checked: value,
									onchange: (event) => {
										const checked = !!event.target.checked;
										TextAreaAutoComplete.enabled = checked;
										setter(checked);
									},
								}),
							]
						),
						$el(
							"label",
							{
								textContent: "Auto-insert comma ",
								style: {
									display: "block",
								},
							},
							[
								$el("input", {
									id: id.replaceAll(".", "-"),
									type: "checkbox",
									checked: !!TextAreaAutoComplete.globalSeparator,
									onchange: (event) => {
										const checked = !!event.target.checked;
										TextAreaAutoComplete.globalSeparator = checked ? ", " : "";
										localStorage.setItem(id + ".AutoSeparate", TextAreaAutoComplete.globalSeparator);
									},
								}),
							]
						),
						$el("button", {
							textContent: "Manage Custom Words",
							onclick: () => {
								app.ui.settings.element.close();
								new CustomWordsDialog().show();
							},
							style: {
								fontSize: "14px",
								display: "block",
								marginTop: "5px",
							},
						}),
					]),
				]);
			},
		});
	},
	beforeRegisterNodeDef(_, def) {
		// Process each input to see if there is a custom word list for
		// { input: { required: { something: ["STRING", { "pysssss.autocomplete": ["groupid", ["custom", "words"] ] }] } } }
		const inputs = { ...def.input?.required, ...def.input?.optional };
		for (const input in inputs) {
			const config = inputs[input][1]?.["pysssss.autocomplete"];
			if (!config) continue;
			if (typeof config === "object" && config.words) {
				const words = {};
				for (const text of config.words || []) {
					const obj = typeof text === "string" ? { text } : text;
					words[obj.text] = obj;
				}
				TextAreaAutoComplete.updateWords(def.name + "." + input, words, false);
			}
		}
	},
});
