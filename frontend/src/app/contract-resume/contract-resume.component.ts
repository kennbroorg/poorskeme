import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-contract-resume',
  templateUrl: './contract-resume.component.html',
  styleUrls: ['./contract-resume.component.scss']
})
export class ContractResumeComponent implements OnInit {

  @Input() public data: any;

  contract: any;
  max_liq_num: number = 0;

  constructor() { 
  }

  ngOnInit(): void {
    this.contract = this.data;
    console.log(`Contract : {this.contract}`, this.data);
    this.max_liq_num = Number((this.contract['max_liq']).toFixed(2));
  }

}
