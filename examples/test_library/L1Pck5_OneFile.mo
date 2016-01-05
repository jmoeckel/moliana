within test_library;
package L1Pck5_OneFile
  package L2Pck1
    package L3Pck1
      model L4Model_good
        parameter Integer n=4;
      equation

      end L4Model_good;

      model L4Model_bad
        Integer p;
      equation

      end L4Model_bad;

      model L4Model_warning
        connector A
        end A;

        parameter Integer a= 1
          annotation(Dialog(connectorSizing=true));
        A conA[a];

      end L4Model_warning;
    end L3Pck1;
  end L2Pck1;

  package L2Pck2_empty
  end L2Pck2_empty;
end L1Pck5_OneFile;
