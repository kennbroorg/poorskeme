import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-contract-collect',
  templateUrl: './contract-collect.component.html',
  styleUrls: ['./contract-collect.component.scss']
})
export class ContractCollectComponent implements OnInit {

  @Input() public data: any;

  contract: any;
  max_liq_num: number = 0;
  fileName: string = '';

  constructor() { 
  }

  ngOnInit(): void {
    this.contract = this.data;
    console.log(`Contract : {this.contract}`, this.data);
    this.max_liq_num = Number((this.contract['max_liq']).toFixed(2));
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      this.fileName = input.files[0].name;
    } else {
      this.fileName = '';
    }
  }
}
