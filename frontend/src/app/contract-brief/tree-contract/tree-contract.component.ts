import { Component, OnInit, ViewChild, ElementRef, Input } from '@angular/core';
import * as d3 from "d3";

@Component({
  selector: 'app-tree-contract',
  templateUrl: './tree-contract.component.html',
  styleUrls: ['./tree-contract.component.scss']
})
export class TreeContractComponent implements OnInit {

  @ViewChild('treecontract', { static: true }) private chartContainer!: ElementRef;
  @Input() public data: any;

  constructor() { }

  ngOnInit() {
    this.renderTreeChart();
  }

  renderTreeChart() {

    let margin = { top: 30, right: 10, bottom: 30, left: 20 };
    let width = 1000;
    let height = 5000;
    let barHeight = 40;
    let barWidth = (width - margin.left - margin.right) * 0.9;
    let element: any = this.chartContainer.nativeElement;

    let i = 0, duration = 400; 
    let root: any;
    let diagonal = d3.linkHorizontal()
      .x((d: any) => { return d.y; })
      .y((d: any) => { return d.x; });

    let svg = d3.select(element).append("svg")
      .attr("width", width) //+ margin.left + margin.right)
      .attr('height', height)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    root = d3.hierarchy(this.data);
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
        .attr("transform", function (d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
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
        .style('stroke', '#fff')
        .style('stroke-width', '2px')
        .attr("d", function (d) {
          var o = { x: source.x0, y: source.y0 };
          return diagonal(<any>{ source: o, target: o });
        });
        // .transition()
        // .duration(duration)
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
      return d._children ? "#D17808" : d.children ? "#D13608" : "#D17808";
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