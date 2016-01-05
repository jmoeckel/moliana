within test_library.L1Pck2;
model L2Model3_warning

  connector A
  end A;

  parameter Integer a= 1
    annotation(Dialog(connectorSizing=true));
  A conA[a];

end L2Model3_warning;
