package com.example.lab3;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        EditText edtx = findViewById(R.id.editTextNumber);
        Spinner spnr = finfViewById(R.id.spinner);
        Button btn = findViewById(R.id.button2);
        TextView txt = findViewById(R.id.textView);

        String[] units=
                {
                        "m to km",
                        "km to m",
                        "cm to m",
                        "m to cm"
                };
// xml or java ko connect krt ha array adapter
        ArrayAdapter<String> adapter1 = new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,units);
        spnr.setAdapter(adapter1);
        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                // EDIT tEXT -->  GRT --> STRING  --> DOUBLE
                double value = Double.parseDouble(edtx.getText().toString());
                String unit = spnr.getSelectedItem().toString();
                double result = 0;

                switch (unit)
                {
                    case "m to km":
                        result=value*1000;
                        break;
                    case "km to m":
                        result = value / 1000;
                        break;
                }


                txt.setText("Result = "  + result);
            }

        });
    }
}