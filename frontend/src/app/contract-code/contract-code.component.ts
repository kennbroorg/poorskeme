import { Component, OnInit, Input } from '@angular/core';
import { HighlightLoader, HighlightAutoResult } from 'ngx-highlightjs';

@Component({
  selector: 'app-contract-code',
  templateUrl: './contract-code.component.html',
  styleUrls: ['./contract-code.component.scss']})
export class ContractCodeComponent implements OnInit {

  @Input() public data: any;

  contract: any;
  highlightedCode : any;
  codeRaw : any;

  response!: HighlightAutoResult;
  code!: string; 

  constructor (private hljsLoader: HighlightLoader) { }

  ngOnInit(): void {
    this.contract = this.data;
    console.log(`Contract : {this.contract}`, this.data);
    this.code = this.contract['SourceCode']
  }

}
