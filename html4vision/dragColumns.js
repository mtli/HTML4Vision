function dragColumns() {
    "use strict";

    var currentFrom = null;

    function isOriginalTable(tbl) {
        return !!(tbl && tbl.classList && tbl.classList.contains("html4vision") && tbl.tBodies && tbl.tBodies.length);
    }

    function bindTh(th, resolveTableFn) {
        if (!th || th.getAttribute("data-drag-bound") === "1") return;
        th.setAttribute("draggable", "true");
        th.setAttribute("data-drag-bound", "1");

        th.addEventListener("dragstart", function (e) {
            e.dataTransfer.effectAllowed = "move";
            var idx = th.cellIndex;
            currentFrom = idx;
            try { e.dataTransfer.setData("text/plain", String(idx)); } catch (err) {}
        });

        th.addEventListener("dragover", function (e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
        });

        th.addEventListener("drop", function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.stopImmediatePropagation) e.stopImmediatePropagation();
            var from = parseInt(e.dataTransfer.getData("text/plain"), 10);
            if (isNaN(from)) from = currentFrom;
            var to = th.cellIndex;
            if (from === to) return;
            var dropTable = th.closest ? th.closest("table") : null;
            var table = resolveTableFn();
            if (!table) return;
            // If dropping on a sticky clone header, sync that header too
            if (dropTable && !isOriginalTable(dropTable)) moveHeaderOnly(dropTable, from, to);
            moveColumn(table, from, to);
            if (window.jQuery && typeof jQuery.fn === "object" && jQuery(table).trigger) {
                try { jQuery(table).trigger("updateAll"); } catch (err) {}
            }
            currentFrom = null;
        });
    }

    function initTable(table) {
        var headerRow = table.tHead && table.tHead.rows.length ? table.tHead.rows[0] : null;
        if (!headerRow) return;

        // Enable dragging on header cells
        for (var i = 0; i < headerRow.cells.length; i++) {
            (function (th) {
                bindTh(th, function () { return table; });
            })(headerRow.cells[i]);
        }
    }

    function moveColumn(table, from, to) {
        var rows = table.rows;
        for (var r = 0; r < rows.length; r++) {
            var cells = rows[r].children; // live HTMLCollection
            if (from >= cells.length || to >= cells.length) continue;
            var fromCell = cells[from];
            // If moving to the right, insert after target cell using nextSibling
            var reference = (to > from) ? cells[to].nextSibling : cells[to];
            rows[r].insertBefore(fromCell, reference);
        }
    }

    function moveHeaderOnly(table, from, to) {
        if (!table || !table.tHead || !table.tHead.rows.length) return;
        var row = table.tHead.rows[0];
        var cells = row.children;
        if (from >= cells.length || to >= cells.length) return;
        var fromCell = cells[from];
        var reference = (to > from) ? cells[to].nextSibling : cells[to];
        row.insertBefore(fromCell, reference);
    }

    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }

    function bindStickyClones() {
        // Bind any header cells not belonging to the original HTML4Vision table (e.g., sticky clones)
        var ths = document.querySelectorAll("thead th");
        for (var i = 0; i < ths.length; i++) {
            var th = ths[i];
            var tbl = th.closest ? th.closest("table") : null;
            if (!tbl) continue;
            if (tbl.classList && tbl.classList.contains("html4vision")) continue; // originals already bound
            bindTh(th, function () { return document.querySelector("table.html4vision"); });
        }
    }

    // Global capturing handlers to ensure drop works on sticky clones and prevent duplicate handling
    document.addEventListener("dragstart", function (e) {
        var th = e.target && e.target.closest ? e.target.closest("th") : null;
        if (!th) return;
        currentFrom = th.cellIndex;
        try { e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", String(currentFrom)); } catch (err) {}
    }, true);

    document.addEventListener("dragover", function (e) {
        var th = e.target && e.target.closest ? e.target.closest("th") : null;
        if (!th) return;
        e.preventDefault();
    }, true);

    document.addEventListener("drop", function (e) {
        var th = e.target && e.target.closest ? e.target.closest("th") : null;
        if (!th) return;
        e.preventDefault();
        e.stopPropagation();
        if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        var tbl = th.closest ? th.closest("table") : null;
        var table = isOriginalTable(tbl) ? tbl : document.querySelector("table.html4vision");
        if (!table) return;
        var from;
        try { from = parseInt(e.dataTransfer.getData("text/plain"), 10); } catch (err) { from = NaN; }
        if (isNaN(from)) from = currentFrom;
        if (from == null) return;
        var to = th.cellIndex;
        if (from === to) return;
        // If dropping on a sticky clone header, sync that header too
        if (tbl && !isOriginalTable(tbl)) moveHeaderOnly(tbl, from, to);
        // Always move original table
        moveColumn(table, from, to);
        if (window.jQuery && typeof jQuery.fn === "object" && jQuery(table).trigger) {
            try { jQuery(table).trigger("updateAll"); } catch (err) {}
        }
        currentFrom = null;
    }, true);

    ready(function () {
        var tables = document.querySelectorAll("table.html4vision");
        for (var i = 0; i < tables.length; i++) {
            initTable(tables[i]);
        }
        bindStickyClones();
        window.addEventListener("scroll", bindStickyClones, { passive: true });
    });
}
