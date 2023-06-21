submit/expense/
    form_input: text(CharField) amount(IntegerField) user_token(CharField)
    output: JsonResponse({status : OK})

submit/income/
    form_input: text(CharField) amount(IntegerField) user_token(CharField)
    output: JsonResponse({status : OK})