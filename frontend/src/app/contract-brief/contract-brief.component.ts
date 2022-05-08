import { Component, OnInit, TemplateRef, ViewChild, ElementRef, ChangeDetectionStrategy, AfterViewInit } from '@angular/core';
import { NbDialogService } from '@nebular/theme';
import { HttpClient } from '@angular/common/http';
import { Color, ScaleType } from '@swimlane/ngx-charts';

import { HighlightLoader, HighlightAutoResult } from 'ngx-highlightjs';
const themeHL: string = 'node_modules/highlight.js/styles/androidstudio.css';

import * as d3 from "d3";

@Component({
  selector: 'app-contract-brief',
  templateUrl: './contract-brief.component.html',
  styleUrls: ['./contract-brief.component.scss']
})
export class ContractBriefComponent implements OnInit {

  @ViewChild('treedata', {read: ElementRef}) treeContainer!: ElementRef<HTMLDivElement>;

  treeData: any;
  contract: any = [];
  view: any = [500, 200];

  colorScheme: Color = { domain: ['#D13608', '#D17808'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  colorSchemeI: Color = { domain: ['#D17808'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  colorSchemeTree: Color = { domain: ['#ac2d06', '#D13608', '#D17808', '#f68b09'], group: ScaleType.Ordinal, selectable: true, name: 'Customer Usage', };
  cardColor: string = 'rgba(0, 0, 0, 0.4)';

  trx: any = [];
  volume: any = [];
  wallets: any = [];
  max_liq: any = [];
  cardNumber: any = [];
  innerPadding : any = [0, 0, 0, 0];
  highlightedCode : any;
  codeRaw : any;

  response!: HighlightAutoResult;

  code = `function myFunction() {
    document.getElementById("demo1").innerHTML = "Test 1!";
    document.getElementById("demo2").innerHTML = "Test 2!";
  }`;

  currentTheme: string = themeHL;

  constructor(private httpClient: HttpClient, 
              private dialogService: NbDialogService,
              private hljsLoader: HighlightLoader) { 
  }

  ngOnInit(): void {
    const url = "http://127.0.0.1:5000/contract"
    this.httpClient
      .get(url)
      .subscribe(this.responseContract,
                 err => console.error('Ops: ', err.message),
                 () => console.log('Completed Contract Info'),
      );
  }

  ngAfterViewInit(): void {
  }

  private responseContract = (data: any): any => {

    // Stats
    this.contract = data
    this.trx = [{"name": "IN", "value": this.contract["trx_in"]}, {"name": "OUT", "value": this.contract["trx_out"]}]
    this.volume = [{"name": "Volume", "value": this.contract["volume"]}]
    this.wallets = [{"name": "Wallets", "value": this.contract["wallets"]}]
    this.max_liq = [{"name": "Max Liquidity - " + this.contract['max_liq_date'], "value": this.contract["max_liq"]}]
    this.cardNumber = [{"name": "Wallets", "value": this.contract["wallets"]}, 
                       {"name": "Max Liquidity", "value": this.contract["max_liq"]}]
    this.code = this.contract['SourceCode']
  }

  open(dialog: TemplateRef<any>) {
    this.dialogService.open(dialog, { context: this.contract });
  }

  statusLabelFormat(c: any): string {
    return `<span style="margin-top: 50px;">${c.label}</span>`;
  }

  renderTreeChart() {

    let margin = { top: 30, right: 10, bottom: 30, left: 20 };
    let width = 960;
    let barHeight = 20;
    let barWidth = (width - margin.left - margin.right) * 0.8;
    let element: any = this.treeContainer.nativeElement;
    console.log("ELEMENT", element);

    let i = 0; 
    var duration = 400;
    var root: any;
    let diagonal = d3.linkHorizontal()
      .x((d: any) => { return d.y; })
      .y((d: any) => { return d.x; });
    // Creates a curved (diagonal) path from parent to the child nodes

    let svg = d3.select(element).append("svg")
      .attr("width", element.offsetWidth) //+ margin.left + margin.right)
      .attr('height', element.offsetHeight)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    this.treeData =
      {
        "name": "Top Level",
        "children": [
          { 
            "name": "Level 2: A",
            "children": [
              { "name": "Son of A" },
              { "name": "Daughter of A" }
            ]
          },
          { "name": "Level 2: B" }
        ]
      }
    console.log("TREE", this.treeData);

    root = d3.hierarchy(this.treeData);
    root.x0 = 0;
    root.y0 = 0;
    moveChildren(root);
    update(root);
  
    function update(source: any) {

      // Compute the flattened node list.
      let nodes = root.descendants();

      let height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom);

      d3.select("svg").transition()
        .duration(duration)
        .attr("height", height);

      d3.select(self.frameElement).transition()
        .duration(duration)
        .style("height", height + "px");

      let index = -1;
      root.eachBefore(function (n: any) {
        n.x = ++index * barHeight;
        n.y = n.depth * 20;
      });

      // Update the nodes…
      let node = svg.selectAll(".node")
        .data(nodes, function (d: any) { return d.id || (d.id = ++i); });

      let nodeEnter = node.enter().append("g")
        .attr("class", "node")
        .attr("transform", function (d: any) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
        .style("opacity", 0);


      // Enter any new nodes at the parent's previous position.
      nodeEnter.append("rect")
        .attr("y", -barHeight / 2)
        .attr("height", barHeight)
        .attr("width", barWidth)
        .style("fill", color)
        .on("click", click);

      nodeEnter.append("text")
        .attr("dy", 5)
        .attr("dx", 5.5)
        .text(function (d: any) { return d.data.name; });

      // Transition nodes to their new position.
      nodeEnter.transition()
        .duration(duration)
        .attr("transform", function (d: any) { return "translate(" + d.y + "," + d.x + ")"; })
        .style("opacity", 1);

      node.transition()
        .duration(duration)
        .attr("transform", function (d: any) { return "translate(" + d.y + "," + d.x + ")"; })
        .style("opacity", 1)
        .select("rect")
        .style("fill", color);

      // Transition exiting nodes to the parent's new position.
      node.exit().transition()
        .duration(duration)
        .attr("transform", function (d: any) { return "translate(" + source.y + "," + source.x + ")"; })
        .style("opacity", 0)
        .remove();

      // Update the links…
      var link = svg.selectAll(".link")
        .data(root.links(), function (d: any) { return d.target.id; });

      // Enter any new links at the parent's previous position.
      link.enter().insert("path", "g")
        .attr("class", "link")
        .style('fill', 'none')
        .style('stroke', '#ccc')
        .style('stroke-width', '2px')
        .attr("d", function (d: any) {
          var o = { x: source.x0, y: source.y0 };
          return diagonal(<any>{ source: o, target: o });
        })
        .transition()
        .duration(duration);
        // .attr("d", diagonal);

      // Transition links to their new position.
      link.transition()
        .duration(duration);
        // .attr("d", diagonal);

      // Transition exiting nodes to the parent's new position.
      link.exit().transition()
        .duration(duration)
        .attr("d", function (d: any) {
          var o = { x: source.x, y: source.y };
          return diagonal(<any>{ source: o, target: o });
        })
        .remove();

      // Stash the old positions for transition.
      root.each(function (d: any) {
        d.x0 = d.x;
        d.y0 = d.y;
      });
    }

    // Toggle children on click.
    function click(d: any) {
      if (d.children) {
        d._children = d.children;
        d.children = null;
      } else {
        d.children = d._children;
        d._children = null;
      }
      update(d);
    }

    function color(d: any) {
      return d._children ? "#3182bd" : d.children ? "#c6dbef" : "#fd8d3c";
    }

    function moveChildren(node: any) { 
      if (node.children) {
        node.children.forEach(function (c: any) { moveChildren(c); });
        node._children = node.children;
        node.children = null;
      }
    }

  }


}
