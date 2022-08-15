import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-diagram',
  templateUrl: './contract-diagram.component.html',
  styleUrls: ['./contract-diagram.component.scss']
})
export class DiagramComponent implements OnInit {

  @Input() public data: any;
  @Input() public h: any;
  @Input() public w: any;

  nodes: any;

  constructor() {}

  ngOnInit() {

    this.nodes = this.data['abi'];
    console.log("Diagram", this.nodes);
  }

}