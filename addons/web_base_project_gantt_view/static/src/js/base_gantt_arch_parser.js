/** @odoo-module */

import { unique } from "@web/core/utils/arrays";
import { visitXML } from "@web/core/utils/xml";
import { archParseBoolean } from "@web/views/utils";

export class BaseGanttArchParser {
    parse(arch) {
        const archInfo = {
            fieldNames: [],
        };

        visitXML(arch, (node) => {
            switch (node.tagName) {
                case "ganttview":
                    this.visitGanttView(node, archInfo);
                    break;
                case "field":
                    this.visitField(node, archInfo);
                    break;
            }
        });

        archInfo.fieldNames = unique(archInfo.fieldNames);
        return archInfo;
    }

    visitGanttView(node, archInfo) {
        
        archInfo.timeFrame = 'Week';

        if (node.hasAttribute("start_date")) {
            archInfo.start_date = node.getAttribute("start_date");
        }
        if (node.hasAttribute("stop_date")) {
            archInfo.stop_date = node.getAttribute("stop_date");
        }
        if (node.hasAttribute("color")) {
            archInfo.color = node.getAttribute("color");
        }
        if (node.hasAttribute("task_progress")) {
            archInfo.task_progress = node.getAttribute("task_progress");
        }
    }
    visitField(node, params) {
        params.fieldNames.push(node.getAttribute("name"));
    }
}
