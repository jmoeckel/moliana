within test_library.L1Pck1.L2Pck1.L3Pck1;
model L4Model_warning

  connector A
  end A;

  parameter Integer a= 1
    annotation(Dialog(connectorSizing=true));
  A conA[a];

end L4Model_warning;
