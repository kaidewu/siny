export interface Benefit {
  benefitName: string;
  benefitCode: string;
  benefitTypeName: string;
  benefitSubtypeName: string;
  isActive: boolean;
  activeDate: string; // Assuming datetime is a string format (ISO 8601)
  createdDate: string;
  isDeleted: boolean;
  deletedDate: string;
}

export interface Filter {
  benefit_name: string;
  benefit_code: string;
  benefit_type_code: string;
  benefit_subtype_code: string;
  active: boolean | true;
  start_created_date: string;
  end_created_date: string;
  deleted: boolean | false;
}
