import { Component, OnInit, Input } from '@angular/core';
import { FileUploadValidators } from '@iplab/ngx-file-upload';
import { FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-contract-collect',
  templateUrl: './contract-collect.component.html',
  styleUrls: ['./contract-collect.component.scss']
})
export class ContractCollectComponent implements OnInit {

  @Input() public data: any;

  contract: any;
  max_liq_num: number = 0;

  public animation: boolean = false;
  public multiple: boolean = false;

  private filesControl = new FormControl<File[]>([], FileUploadValidators.filesLimit(2));

  public demoForm = new FormGroup({
      files: this.filesControl
  });

  constructor() {
  }

  ngOnInit(): void {
    this.contract = this.data;
    console.log(`Contract : {this.contract}`, this.data);
  }

  public toggleStatus(): void {
      this.filesControl.disabled ? this.filesControl.enable() : this.filesControl.disable();
  }

  public toggleMultiple() {
      this.multiple = !this.multiple;
  }

  public clear(): void {
      this.filesControl.setValue([]);
  }

  process(caddress: any, bfrom: any, bto: any) {
    console.log("Apreto", caddress, bfrom, bto, this.filesControl, this.demoForm);
    const files = this.filesControl.value;
    if (files && files.length > 0) {
      console.log("Archivos cargados:", files);
      // Aquí puedes pasar los archivos al app.component o enviarlos directamente al backend
    } else {
      console.log("No se ha cargado ningún archivo.");
    }
  }
}
