import { Component, OnInit, Input } from '@angular/core';
import { HighlightLoader, HighlightAutoResult } from 'ngx-highlightjs';
// const themeHL: string = 'node_modules/highlight.js/styles/arduino-light.css';
              // '../../../node_modules/highlight.js/styles/arduino-light.css']

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
  //  = `function myFunction() {
  //   document.getElementById("demo1").innerHTML = "Test 1!";
  //   document.getElementById("demo2").innerHTML = "Test 2!";
  // }`;

  // currentTheme: string = themeHL;

  constructor (private hljsLoader: HighlightLoader) { 
  }


  ngOnInit(): void {
    this.contract = this.data;
    console.log(`Contract : {this.contract}`, this.data);
    this.code = this.contract['SourceCode']
    // console.log(`Theme : {this.currentTheme}`, this.currentTheme);
  }

}
